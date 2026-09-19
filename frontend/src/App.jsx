import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import QueryHistory from './components/QueryHistory';
import {
  register,
  login,
  getDocuments,
  deleteDocument,
  healthCheck,
  setToken,
  getToken,
} from './services/api';

export default function App() {
  const [user, setUser] = useState(null);
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [docError, setDocError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  const checkApiHealth = async () => {
    try {
      await healthCheck();
      setApiStatus('connected');
    } catch {
      setApiStatus('disconnected');
    }
  };

  // Check API health on mount, then poll
  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Restore session and load documents if a token exists
  useEffect(() => {
    if (getToken()) {
      fetchDocuments();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await getDocuments();
      setDocuments(response.data);
      setDocError(null);
    } catch (err) {
      if (err.response?.status === 401) {
        handleLogout();
        return;
      }
      setDocError(err.response?.data?.detail || 'Failed to load documents');
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();

    if (!username.trim() || !password) {
      setError('Username and password are required');
      return;
    }
    if (mode === 'register' && !email.trim()) {
      setError('Email is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (mode === 'register') {
        const response = await register({
          username: username.trim(),
          email: email.trim(),
          password,
        });
        const loginResponse = await login(username.trim(), password);
        setToken(loginResponse.data.access_token);
        setUser(loginResponse.data.user);
      } else {
        const response = await login(username.trim(), password);
        setToken(response.data.access_token);
        setUser(response.data.user);
      }
      setPassword('');
      fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    setDocuments([]);
    setUsername('');
    setEmail('');
    setPassword('');
    setError(null);
    setDocError(null);
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await deleteDocument(docId);
      setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
    } catch (err) {
      setDocError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const handleUploadSuccess = (uploadedDoc) => {
    setDocuments((prev) => [...prev, { ...uploadedDoc, total_chunks: uploadedDoc.total_chunks }]);
  };

  const authForm = (
    <div className="max-w-md mx-auto mb-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">
          {mode === 'login' ? 'Welcome back' : 'Create an account'}
        </h2>

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g., john_doe"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              disabled={loading}
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className="block text-gray-700 font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g., john@example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                disabled={loading}
              />
            </div>
          )}

          <div>
            <label className="block text-gray-700 font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === 'register' ? 'At least 8 characters' : 'Your password'}
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
            disabled={loading || !username.trim() || !password}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Sign up'}
          </button>
        </form>

        <button
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setError(null);
          }}
          className="mt-4 text-sm text-blue-600 hover:text-blue-700"
        >
          {mode === 'login'
            ? "Don't have an account? Sign up"
            : 'Already have an account? Log in'}
        </button>
      </div>
    </div>
  );

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

        {!user ? (
          authForm
        ) : (
          <>
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-800">
                Welcome, {user.username}!
              </h2>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-800 font-medium"
              >
                Log out
              </button>
            </div>

            {documents.length > 0 && (
              <div className="mb-6 bg-white rounded-lg shadow p-4">
                <p className="text-blue-900 mb-2">
                  <span className="font-semibold">{documents.length}</span>{' '}
                  document(s) uploaded
                </p>
                <ul className="divide-y divide-gray-100">
                  {documents.map((doc) => (
                    <li key={doc.id} className="flex justify-between items-center py-2">
                      <span className="text-sm text-gray-700">{doc.filename}</span>
                      <span className="flex items-center gap-3">
                        <span className="text-xs text-gray-400">
                          {doc.total_chunks} chunks
                        </span>
                        <button
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="text-xs text-red-600 hover:text-red-700"
                        >
                          Delete
                        </button>
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {docError && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {docError}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-1 space-y-6">
                <DocumentUpload onUploadSuccess={handleUploadSuccess} />
                <QueryHistory />
              </div>

              {/* Right Column */}
              <div className="lg:col-span-2">
                <ChatInterface documentIds={documents.map((doc) => doc.id)} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
