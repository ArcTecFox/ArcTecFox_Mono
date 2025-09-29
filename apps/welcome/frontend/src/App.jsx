import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import React, { Suspense } from "react";
import { HelmetProvider } from "react-helmet-async";

// Eager load Home for fast first paint
import Home from "./pages/Home";
import Login from "./pages/Login";
import UnifiedLayout from "./layouts/UnifiedLayout";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import ErrorBoundary from "./components/ErrorBoundary";
import LoadingSpinner from "./components/ui/LoadingSpinner";

// Lazy load all other pages (code splitting)
const MaintenanceSchedule = React.lazy(() => import("./components/dashboard/maintenance-schedule"));
const UserManagement = React.lazy(() => import("./pages/UserManagement"));
const CompanyManagement = React.lazy(() => import("./pages/CompanyManagement"));
const SuperAdminManagement = React.lazy(() => import("./pages/SuperAdminManagement"));
const TermsOfService = React.lazy(() => import("./pages/TermsOfService"));
const PrivacyPolicy = React.lazy(() => import("./pages/PrivacyPolicy"));
const AcceptInvitation = React.lazy(() => import("./pages/AcceptInvitation"));

const FAQ = React.lazy(() => import("./pages/FAQ"));
const ApprovedSignup = React.lazy(() => import("./pages/ApprovedSignup"));


function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner text="Authenticating..." />;
  if (!user) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  React.useEffect(() => {
    const handleVisibilityChange = () => {};
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  return (
    <ErrorBoundary>
      <HelmetProvider>
        <Router>
          <AuthProvider>
            <Suspense fallback={<LoadingSpinner text="Loading page..." />}>
              <Routes>

              {/* All routes use UnifiedLayout for consistent navigation */}
              <Route element={<UnifiedLayout />}>
                {/* Public routes */}
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/faq" element={<FAQ />} /> {/* ← new FAQ route */}
                <Route path="/terms-of-service" element={<TermsOfService />} />
                <Route path="/privacy-policy" element={<PrivacyPolicy />} />
                <Route path="/accept-invitation/:token" element={<AcceptInvitation />} />
                <Route path="/approved-signup" element={<ApprovedSignup />} />
                
                {/* Protected routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <MaintenanceSchedule />
                  </ProtectedRoute>
                } />
                <Route path="/admin/users" element={
                  <ProtectedRoute>
                    <UserManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/companies" element={
                  <ProtectedRoute>
                    <CompanyManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/super-admins" element={
                  <ProtectedRoute>
                    <SuperAdminManagement />
                  </ProtectedRoute>
                } />
              </Route>
            </Routes>
          </Suspense>
        </AuthProvider>
      </Router>
    </HelmetProvider>

    </ErrorBoundary>
  );
}
