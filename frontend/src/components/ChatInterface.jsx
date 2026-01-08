import React, { useState, useRef, useEffect } from 'react';
import { queryDocuments } from '../services/api';

export default function ChatInterface({ userId, documentIds = [] }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim()) {
      return;
    }

    if (!userId) {
      setError('User ID is required');
      return;
    }

    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const queryPayload = {
        user_id: userId,
        query_text: input,
      };

      if (documentIds.length > 0) {
        queryPayload.document_ids = documentIds;
      }

      const response = await queryDocuments(queryPayload);

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        chunks: response.data.retrieved_chunks,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'error',
        content: err.response?.data?.detail || 'Failed to get response',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setError('Failed to send query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow flex flex-col h-[600px]">
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h2 className="text-2xl font-bold">Ask Questions</h2>
        <p className="text-blue-100 text-sm">Query your documents with AI</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>No messages yet. Start by asking a question about your documents.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.role === 'error'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              {msg.chunks && msg.chunks.length > 0 && (
                <div className="mt-2 text-xs border-t border-current border-opacity-20 pt-2">
                  <p className="font-semibold">Sources:</p>
                  <ul className="list-disc list-inside">
                    {msg.chunks.slice(0, 3).map((chunk, i) => (
                      <li key={i} className="text-opacity-75">
                        Doc {chunk.document_id}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="bg-red-50 border-t border-red-200 text-red-700 px-4 py-3">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t p-4 bg-gray-50 rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
