import React, { useState, useEffect } from 'react';
import { getQueryHistory } from '../services/api';

export default function QueryHistory({ userId }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (userId) {
      fetchHistory();
    }
  }, [userId]);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getQueryHistory(userId);
      setHistory(response.data.history || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load query history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Query History</h2>
        <button
          onClick={fetchHistory}
          disabled={loading}
          className="text-blue-600 hover:text-blue-700 disabled:text-gray-400"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-8 text-gray-500">
          Loading query history...
        </div>
      )}

      {!loading && history.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No query history yet. Start by asking questions!
        </div>
      )}

      {!loading && history.length > 0 && (
        <div className="space-y-4 max-h-[500px] overflow-y-auto">
          {history.map((item, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <p className="font-semibold text-gray-800">{item.query_text}</p>
                <span className="text-xs text-gray-500">
                  {formatDate(item.created_at)}
                </span>
              </div>
              <p className="text-gray-600 text-sm mb-2">{item.response}</p>
              <div className="text-xs text-gray-500">
                Retrieved {item.retrieved_chunks_count || 0} chunk(s)
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
