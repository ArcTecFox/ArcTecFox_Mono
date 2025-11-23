import React, { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import SEO from "../components/SEO";

export default function ConfirmEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading');
  const [errorType, setErrorType] = useState('');

  useEffect(() => {
    // Check URL params for status or error
    const statusParam = searchParams.get('status');
    const errorParam = searchParams.get('error');

    if (statusParam === 'success') {
      setStatus('success');
    } else if (statusParam === 'already_confirmed') {
      setStatus('already_confirmed');
    } else if (errorParam) {
      setStatus('error');
      setErrorType(errorParam);
    } else {
      // If no params, assume loading (backend is processing)
      setStatus('loading');
    }
  }, [searchParams]);

  const getErrorMessage = () => {
    switch (errorType) {
      case 'expired':
        return 'This confirmation link has expired. Confirmation links are valid for 24 hours.';
      case 'invalid':
        return 'This confirmation link is invalid. Please request a new plan.';
      case 'pdf_failed':
        return 'Your email was confirmed, but we had trouble generating your PM plan PDF. Please contact support.';
      case 'email_failed':
        return 'Your email was confirmed, but we had trouble sending your PM plan. Please contact support.';
      case 'server_error':
        return 'An error occurred while processing your confirmation. Please try again or contact support.';
      default:
        return 'An error occurred during confirmation. Please try again or contact support.';
    }
  };

  return (
    <>
      <SEO
        title="Confirm Your Email | ArcTecFox"
        description="Confirm your email to receive your free preventive maintenance plan"
        noindex={true}
      />

      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">

          {status === 'loading' && (
            <>
              <div className="flex justify-center mb-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Confirming Your Email
              </h2>
              <p className="text-gray-600">
                Please wait while we verify your email address...
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Email Confirmed!
              </h2>

              <p className="text-gray-600 mb-6">
                Your preventive maintenance plan has been sent to your email inbox.
                You should receive it within the next few minutes.
              </p>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
                <p className="text-sm text-blue-900 font-semibold mb-2">
                  What's next?
                </p>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Check your email for the PDF with your complete PM plan</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Review the 12 comprehensive maintenance tasks</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Share the plan with your maintenance team</span>
                  </li>
                </ul>
              </div>

              <Link
                to="/"
                className="inline-block w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
              >
                Return to Home
              </Link>

              <p className="text-sm text-gray-500 mt-4">
                Don't see the email? Check your spam folder.
              </p>
            </>
          )}

          {status === 'already_confirmed' && (
            <>
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Already Confirmed
              </h2>

              <p className="text-gray-600 mb-6">
                This email has already been confirmed. Your PM plan should already be in your inbox.
              </p>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-gray-700">
                  If you didn't receive your PM plan, please check your spam folder or contact our support team.
                </p>
              </div>

              <div className="space-y-3">
                <Link
                  to="/"
                  className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  Return to Home
                </Link>

                <a
                  href="mailto:support@arctecfox.co"
                  className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                >
                  Contact Support
                </a>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Confirmation Failed
              </h2>

              <p className="text-gray-600 mb-6">
                {getErrorMessage()}
              </p>

              <div className="space-y-3">
                <Link
                  to="/#pm-planner-section"
                  className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  {errorType === 'expired' ? 'Generate New Plan' : 'Try Again'}
                </Link>

                <a
                  href="mailto:support@arctecfox.co"
                  className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-semibold"
                >
                  Contact Support
                </a>
              </div>
            </>
          )}

        </div>
      </div>
    </>
  );
}
