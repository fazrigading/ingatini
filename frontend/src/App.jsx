import React, { useState, useEffect } from 'react';
import './App.css';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import QueryHistory from './components/QueryHistory';
import { createUser, getDocuments, healthCheck } from './services/api';

export default function App() {
  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await healthCheck();
      setApiStatus('connected');
    } catch (err) {
      setApiStatus('disconnected');
    }
  };

  const handleCreateOrGetUser = async (e) => {
    e.preventDefault();

    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await createUser({
        username: username,
        email: `${username}@ingatini.local`,
      });
      setUserId(response.data.id);
      fetchDocuments(response.data.id);
      setUsername('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async (id) => {
    try {
      const response = await getDocuments(id);
      setDocuments(response.data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleUploadSuccess = (uploadedDoc) => {
    setDocuments((prev) => [...prev, uploadedDoc]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Ingatini RAG
          </h1>
          <p className="text-gray-600">
            Retrieval-Augmented Generation for Intelligent Document Q&A
          </p>
        </div>

        {/* API Status */}
        <div className="mb-6">
          <div
            className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
              apiStatus === 'connected'
                ? 'bg-green-100 text-green-800'
                : apiStatus === 'disconnected'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            <span className="w-2 h-2 rounded-full mr-2 bg-current"></span>
            {apiStatus === 'connected'
              ? 'API Connected'
              : apiStatus === 'disconnected'
              ? 'API Disconnected'
              : 'Checking...'}
          </div>
        </div>

        {!userId ? (
          // User Setup Section
          <div className="max-w-md mx-auto mb-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">
                Get Started
              </h2>

              <form onSubmit={handleCreateOrGetUser} className="space-y-4">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Enter your username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g., john_doe"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                    disabled={loading}
                  />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !username.trim()}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {loading ? 'Creating...' : 'Continue'}
                </button>
              </form>
            </div>
          </div>
        ) : (
          // Main Application Section
          <>
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-800">
                Welcome, {username || `User ${userId}`}!
              </h2>
              <button
                onClick={() => setUserId(null)}
                className="text-gray-600 hover:text-gray-800 font-medium"
              >
                Switch User
              </button>
            </div>

            {documents.length > 0 && (
              <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-900">
                  <span className="font-semibold">{documents.length}</span>{' '}
                  document(s) uploaded
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-1 space-y-6">
                <DocumentUpload
                  userId={userId}
                  onUploadSuccess={handleUploadSuccess}
                />
                <QueryHistory userId={userId} />
              </div>

              {/* Right Column */}
              <div className="lg:col-span-2">
                <ChatInterface
                  userId={userId}
                  documentIds={documents.map((doc) => doc.id)}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
