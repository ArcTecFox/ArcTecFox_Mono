import { useState } from 'react';
import { createAccessRequest } from '../api';

export default function RequestAccessModal({ isOpen, onClose }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('[RequestAccess] Submitting request for:', email);

      const response = await createAccessRequest({
        email: email.trim(),
        full_name: 'Test User', // Hardcoded as requested
        lead_id: null // No PM plan dependency
      });

      console.log('[RequestAccess] Success:', response);
      setSuccess(true);

      // Auto-close after 3 seconds
      setTimeout(() => {
        onClose();
        setEmail('');
        setSuccess(false);
      }, 3000);

    } catch (err) {
      console.error('[RequestAccess] Error:', err);

      // Enhanced error logging for Supabase issues
      if (err.response) {
        console.error('[RequestAccess] Response error:', {
          status: err.response.status,
          data: err.response.data,
          headers: err.response.headers
        });
      }

      setError(err.response?.data?.detail || 'Failed to submit request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEmail('');
    setError(null);
    setSuccess(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Request Access</h2>

        {success ? (
          <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
            <p className="text-green-800">
              ✓ Request submitted! Check your email for next steps.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="you@example.com"
                disabled={loading}
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Request Access'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
