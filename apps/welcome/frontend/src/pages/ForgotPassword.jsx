import React, { useState } from "react";
import { Link } from "react-router-dom";
import { resetPasswordForEmail } from "../api";
import SEO from "../components/SEO";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await resetPasswordForEmail(email);
      setSubmitted(true);
    } catch (err) {
      // Still show success message for security reasons
      // Don't reveal whether the email exists or not
      console.error("Password reset error:", err);
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO
        title="Forgot Password"
        description="Reset your ArcTecFox password"
        noindex={true}
      />
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">Reset Password</h2>
            <p className="mt-2 text-sm text-gray-600">
              Enter your email address and we'll send you a password reset link
            </p>
          </div>

          {!submitted ? (
            <form className="space-y-4 mt-6" onSubmit={handleSubmit}>
              {error && <p className="text-red-500 text-center text-sm">{error}</p>}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full p-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Sending..." : "Send Reset Link"}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <p className="text-green-800 text-sm font-medium">
                  If that email has a password set up, we've sent a reset link. Please check your inbox.
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <p className="text-blue-800 text-sm">
                  <strong>Note:</strong> If you don't have a password set up (e.g., Google Sign-In only),
                  please contact your administrator for access.
                </p>
              </div>
            </div>
          )}

          <div className="text-center space-y-2 mt-6">
            <p className="text-sm text-gray-600">
              Remember your password?{" "}
              <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
                Back to Login
              </Link>
            </p>

            {!submitted && (
              <p className="text-sm text-gray-600">
                Need access?{" "}
                <Link to="/" className="text-blue-600 hover:text-blue-800">
                  Request Access
                </Link>
              </p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ForgotPassword;
