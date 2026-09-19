import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:8000/api"

TEST_USER = {
    "username": "test_user_1",
    "email": "test_user_1@example.com"
}

TEST_QUERY = "What is the main topic of the document?"


def test_health_check():
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")
    return response.json()


def test_create_user():
    print("\n👤 Creating Test User...")
    response = requests.post(
        f"{API_BASE_URL}/users/",
        json=TEST_USER
    )
    
    if response.status_code == 400:
        print("⚠️  User already exists, fetching existing user...")
        # Try to list users
        response = requests.get(f"{API_BASE_URL}/users/")
        users = response.json()
        if users:
            user_id = users[0]["id"]
        else:
            raise Exception("No users found and couldn't create one")
    else:
        assert response.status_code == 201 or response.status_code == 200
        user_id = response.json()["id"]
    
    print(f"✅ User created/found with ID: {user_id}")
    return user_id


def test_upload_document(user_id: int, file_path: str):
    print(f"\n📄 Uploading Document: {file_path}...")
    
    if not Path(file_path).exists():
        print(f"⚠️  File not found: {file_path}")
        print("Creating sample test document...")
        
        # Create a sample text file
        sample_path = "test_document.txt"
        with open(sample_path, "w") as f:
            f.write("""
Ingatini: A Personal Knowledge Search Engine

Ingatini is a Retrieval-Augmented Generation (RAG) application designed to help users
upload documents and ask questions about them using artificial intelligence.

Key Features:
- Document upload support (PDF, DOCX, TXT)
- Automatic text extraction and embedding
- Vector similarity search
- AI-powered question answering with source attribution
- Query history tracking

Technical Stack:
- Backend: FastAPI with Python
- Database: PostgreSQL with pgvector
- AI: LangChain with Gemini API
- Embeddings: text-embedding-3-small model

How It Works:
1. Users upload documents to the system
2. The system extracts text and splits it into chunks
3. Each chunk is converted to a vector embedding
4. When users ask questions, embeddings are searched for similar chunks
5. Relevant chunks are combined and sent to an LLM for augmented responses
6. The LLM generates answers with citations to source documents

Benefits:
- Efficient knowledge retrieval from large documents
- Automated content search without manual indexing
- Natural language question answering
- Source attribution for all answers
            """)
        file_path = sample_path
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f, "text/plain")}
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            params={"user_id": user_id},
            files=files
        )
    
    assert response.status_code == 200
    doc_data = response.json()
    doc_id = doc_data["id"]
    chunk_count = doc_data["total_chunks"]
    
    print(f"✅ Document uploaded - ID: {doc_id}, Chunks: {chunk_count}")
    return doc_id, chunk_count


def test_list_documents(user_id: int):
    print(f"\n📚 Listing Documents for User {user_id}...")
    
    response = requests.get(f"{API_BASE_URL}/documents/{user_id}")
    assert response.status_code == 200
    
    documents = response.json()
    print(f"✅ Found {len(documents)} document(s)")
    
    for doc in documents:
        print(f"  - {doc['filename']} ({doc['total_chunks']} chunks)")
    
    return documents


def test_query_documents(user_id: int, query_text: str = TEST_QUERY):
    print(f"\n🔍 Querying Documents...")
    print(f"Query: {query_text}")
    
    response = requests.post(
        f"{API_BASE_URL}/query/",
        json={
            "user_id": user_id,
            "query_text": query_text
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    
    print(f"✅ Query processed")
    print(f"Response: {result['response'][:200]}...")
    print(f"Retrieved chunks: {len(result['retrieved_chunks'])}")
    
    return result


def test_query_history(user_id: int):
    print(f"\n📋 Fetching Query History for User {user_id}...")
    
    response = requests.get(f"{API_BASE_URL}/query/history/{user_id}")
    assert response.status_code == 200
    
    history = response.json()["history"]
    print(f"✅ Found {len(history)} previous query/queries")
    
    for log in history[:3]:
        print(f"  - Q: {log['query'][:50]}...")
    
    return history


def run_all_tests():
    print("=" * 60)
    print("🚀 Ingatini RAG Pipeline Test Suite")
    print("=" * 60)
    
    try:
        test_health_check()
        user_id = test_create_user()
        doc_id, chunk_count = test_upload_document(user_id, "test_document.txt")
        test_list_documents(user_id)
        test_query_documents(user_id)
        test_query_documents(user_id, "What is the technical stack?")
        test_query_documents(user_id, "How does the system work?")
        test_query_history(user_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error - Make sure the server is running:")
        print("   docker compose up")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
