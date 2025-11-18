import React, { useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { signIn, signUp, signInWithGoogle, isProfileComplete, validatePassword, shouldUseGoogleAuth, updatePassword } from "../api";
import { useAuth } from "../hooks/useAuth";

function Login() {
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState("");
  const [passwordErrors, setPasswordErrors] = useState([]);
  const [isInviteFlow, setIsInviteFlow] = useState(false);
  const navigate = useNavigate();
  const { loginWithGoogle, user } = useAuth();

  // Detect invite flow from URL parameter
  useEffect(() => {
    const inviteParam = searchParams.get('invite');
    const hash = window.location.hash;

    if (inviteParam === 'true' || hash.includes('type=invite') || hash.includes('type=recovery')) {
      console.log('🔑 Invite/recovery flow detected');
      setIsInviteFlow(true);
      setConfirmationMessage("Welcome! Please set your password to complete your account setup.");
    }
  }, [searchParams]);

  // Check for Gmail email on email change
  const handleEmailChange = (e) => {
    const emailValue = e.target.value;
    setEmail(emailValue);

    if (shouldUseGoogleAuth(emailValue)) {
      setError("Gmail addresses should use Google Sign-In. Please use the Google button below.");
    } else {
      setError(null);
    }
  };

  // Validate password on change
  const handlePasswordChange = (e) => {
    const passwordValue = e.target.value;
    setPassword(passwordValue);

    if (isSignUp && passwordValue) {
      const validation = validatePassword(passwordValue);
      setPasswordErrors(validation.errors);
    } else {
      setPasswordErrors([]);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await loginWithGoogle();
      if (result.success) {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
      console.error("Google login error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSetup = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Validate password
    if (!password || password.length < 6) {
      setError("Password must be at least 6 characters long");
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    const validation = validatePassword(password);
    if (!validation.valid) {
      setError("Password requirements not met: " + validation.errors.join(", "));
      setLoading(false);
      return;
    }

    try {
      console.log('🔐 Setting password for invited user...');
      await updatePassword(password);
      setConfirmationMessage("✅ Password set successfully! Redirecting to dashboard...");
      setLoading(false);
      // Redirect to dashboard after successful password setup
      setTimeout(() => {
        console.log('✅ Password set successfully, redirecting to dashboard');
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      console.error("❌ Password setup error:", err);
      setError(err.message || "Failed to set password. Please try again.");
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Check if Gmail email
    if (shouldUseGoogleAuth(email)) {
      setError("Gmail addresses must use Google Sign-In. Please use the Google button.");
      setLoading(false);
      return;
    }

    if (isSignUp && password !== confirmPassword) {
      setError("Passwords do not match!");
      setLoading(false);
      return;
    }

    // Validate password for signup
    if (isSignUp) {
      const validation = validatePassword(password);
      if (!validation.valid) {
        setError("Password requirements not met: " + validation.errors.join(", "));
        setLoading(false);
        return;
      }
    }

    try {
      if (isSignUp) {
        await signUp(email, password);
        setConfirmationMessage("✅ Check your email to confirm your account and complete 2FA setup!");
      } else {
        try {
          const user = await signIn(email, password);
          if (!user) {
            throw new Error("No user data returned");
          }
          // Skip profile completion check - redirect directly to dashboard
          navigate("/dashboard");
        } catch (err) {
          console.error("Sign in error:", err);
          setError(err.message);
        }
      }
    } catch (err) {
      setError(err.message);
      console.error("❌ Authentication Error:", err.message);
    } finally {
      setLoading(false);
    }
  };

  // Show password setup form for invite flow
  if (isInviteFlow) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome to ArcTecFox!</h2>
            <p className="text-gray-600">Set your password to complete your account setup</p>
          </div>

          {confirmationMessage && <p className="text-green-500 text-center text-sm">{confirmationMessage}</p>}
          {error && <p className="text-red-500 text-center text-sm">{error}</p>}

          <form className="space-y-4 mt-6" onSubmit={handlePasswordSetup}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Create Password
              </label>
              <input
                type="password"
                required
                className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                value={password}
                onChange={handlePasswordChange}
                minLength={6}
              />
              <p className="text-xs text-gray-500 mt-1">Must be at least 6 characters</p>
              {passwordErrors.length > 0 && (
                <div className="mt-2 text-sm text-red-600">
                  <p className="font-medium">Password requirements:</p>
                  <ul className="list-disc list-inside">
                    {passwordErrors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                required
                className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading || passwordErrors.length > 0}
              className="w-full p-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Setting password..." : "Set Password & Continue"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              By setting your password, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
        <h2 className="text-center text-3xl font-bold text-gray-900">
          {isSignUp ? "Create an Account" : "Sign In"}
        </h2>
        {confirmationMessage && <p className="text-green-500 text-center">{confirmationMessage}</p>}
        {error && <p className="text-red-500 text-center text-sm">{error}</p>}

        {/* Google Sign In */}
        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 p-3 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>

        <div className="flex items-center">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="px-3 text-gray-500 text-sm">OR</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <input
              type="email"
              required
              className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Work email (non-Gmail)"
              value={email}
              onChange={handleEmailChange}
            />
          </div>

          <div>
            <input
              type="password"
              required
              className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Password"
              value={password}
              onChange={handlePasswordChange}
            />
            {isSignUp && passwordErrors.length > 0 && (
              <div className="mt-2 text-sm text-red-600">
                <p className="font-medium">Password requirements:</p>
                <ul className="list-disc list-inside">
                  {passwordErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
            {!isSignUp && (
              <div className="mt-2 text-right">
                <Link to="/forgot-password" className="text-sm text-blue-600 hover:text-blue-800">
                  Forgot Password?
                </Link>
              </div>
            )}
          </div>

          {isSignUp && (
            <div>
              <input
                type="password"
                required
                className="block w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading || (isSignUp && passwordErrors.length > 0) || shouldUseGoogleAuth(email)}
            className="w-full p-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Loading..." : isSignUp ? "Sign Up" : "Sign In"}
          </button>
        </form>

        <div className="text-center space-y-2">
          <p className="text-sm text-gray-600">
            {isSignUp ? "Already have an account? " : "Don't have an account? "}
            <button onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
              setPasswordErrors([]);
              setConfirmationMessage("");
            }} className="text-blue-600 hover:text-blue-800">
              {isSignUp ? "Sign In" : "Sign Up"}
            </button>
          </p>

          {!isSignUp && (
            <p className="text-sm text-gray-600">
              Need access? <Link to="/" className="text-blue-600 hover:text-blue-800">Request Access</Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
