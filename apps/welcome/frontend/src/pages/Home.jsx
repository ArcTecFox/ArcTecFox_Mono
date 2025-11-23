import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import LeadCaptureModal from "../components/LeadCaptureModal";
import PMPlannerOpen from "../pages/PMPlannerOpen";
import ProgressBar from "../components/ProgressBar";
import ParentPlanLoadingModal from "../components/assets/ParentPlanLoadingModal";
import { captureLeadWithPlan } from "../api";
import { useToast } from "../hooks/use-toast";
import SEO from "../components/SEO";
import { Helmet } from "react-helmet-async";

export default function Home() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  const [showLeadModal, setShowLeadModal] = useState(false);
  const [showLoadingModal, setShowLoadingModal] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('analyzing');
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [assetName, setAssetName] = useState("");
  const [completion, setCompletion] = useState(0);
  const [formState, setFormState] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [resetFormTrigger, setResetFormTrigger] = useState(0);
  const [emailSent, setEmailSent] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    if (!loading && user) navigate("/dashboard", { replace: true });
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4" />
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  const scrollToGenerator = () => {
    const el = document.getElementById("pm-planner-section");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  const handlePlannerProgress = (formData) => {
    setFormState(formData);
    setAssetName(formData?.name || "");
    const keys = [
      "name",
      "model",
      "serial",
      "category",
      "hours",
      "additional_context",
      "environment",
      "date_of_plan_start",
    ];
    const filled = keys.filter((k) => {
      const v = formData?.[k];
      return v !== undefined && String(v).trim() !== "";
    }).length;
    setCompletion(Math.round((filled / keys.length) * 100));
  };

  const handlePlannerSubmit = async (formData) => {
    setFormState(formData);
    setShowLeadModal(true);
  };

  const handleLeadSubmit = async ({ email, company, fullName, requestAccess }) => {
    try {
      setSubmitting(true);


      setShowLeadModal(false);
      setShowLoadingModal(true);

      // Simulate loading progression
      const progressSteps = [
        { status: 'analyzing', progress: 25, delay: 800 },
        { status: 'generating', progress: 50, delay: 1200 },
        { status: 'creating', progress: 75, delay: 1000 },
        { status: 'saving', progress: 90, delay: 500 }
      ];

      for (const step of progressSteps) {
        setLoadingStatus(step.status);
        setLoadingProgress(step.progress);
        await new Promise(resolve => setTimeout(resolve, step.delay));
      }

      // Call the backend endpoint that handles everything
      const result = await captureLeadWithPlan({
        planData: formState,
        email,
        company,
        fullName,
        requestAccess
      });

      setLoadingProgress(100);
      await new Promise(resolve => setTimeout(resolve, 300));
      setShowLoadingModal(false);

      // Show success state instead of form
      setEmailSent(true);
      setSubmittedEmail(email);

      // Clear the form state
      setResetFormTrigger(prev => prev + 1);
      setAssetName("");
      setCompletion(0);
      setFormState(null);

    } catch (err) {
      console.error("❌ Lead capture failed:", err);
      setShowLoadingModal(false);
      toast({
        title: "Plan Generation Failed",
        description: `Failed to generate plan: ${err.message}`,
        variant: "destructive"
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title="Free Preventive Maintenance Plan Generator | ArcTecFox"
        description="ArcTecFox delivers structured, CMMS-ready preventive maintenance plans in under 2 minutes. Plan, Prevent, Perform — keep assets under management reliable and compliant."
      />

      <div className="bg-gray-50 relative font-sans">
        {/* HERO */}
        <section className="bg-white py-16 text-center border-b">
          <div className="max-w-5xl mx-auto px-4">
            <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-6">
              Failing to plan is planning to fail.
            </h1>
            <p className="text-lg text-gray-700 mb-8 max-w-3xl mx-auto leading-relaxed">
              ArcTecFox provides the most effective preventive maintenance plans in the industry — prevent failure before it happens, optimize reliability, and scale maintenance with confidence.
            </p>
            <div className="flex flex-col items-center justify-center gap-3">
              <button
                onClick={scrollToGenerator}
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 shadow"
              >
                <span>⚡</span> Generate My Free PM Plan
              </button>
              <Link to="/faq" className="text-blue-600 font-semibold hover:underline">
                See FAQs
              </Link>
            </div>
            <p className="text-sm text-gray-600 mt-3">Plan, Prevent, Perform.</p>
          </div>
        </section>

        {/* PAIN POINTS */}
        <section className="py-12 text-center">
          <div className="max-w-5xl mx-auto px-4">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">Why teams fall behind</h2>
            <ul className="grid gap-3 text-left sm:grid-cols-3 text-gray-800">
              <li className="bg-white p-4 rounded border">Incomplete CMMS setups create gaps in coverage.</li>
              <li className="bg-white p-4 rounded border">Outdated spreadsheets ignore real operating conditions.</li>
              <li className="bg-white p-4 rounded border">Unstructured work increases downtime and costs.</li>
            </ul>
          </div>
        </section>

        {/* SOLUTION */}
        <section className="bg-white py-12 border-y">
          <div className="max-w-5xl mx-auto px-4">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3">Continuous PM Optimization</h2>
            <p className="text-gray-700 mb-6">
              A preventive maintenance plan is not a one-time document. It's a structured, evolving program aligned to your assets under management.
            </p>
            <div className="grid sm:grid-cols-3 gap-6 text-left">
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Quarterly reviews</h3>
                <p className="text-gray-700">Refine tasks and intervals based on reliability performance and compliance.</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Lifecycle updates</h3>
                <p className="text-gray-700">Revise plans as assets are installed, upgraded, or decommissioned.</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Data-driven revisions</h3>
                <p className="text-gray-700">Leverage standards, field data, and technician feedback to stay effective.</p>
              </div>
            </div>
          </div>
        </section>


        {/* FAQ ABOVE GENERATOR */}
        <section className="bg-gray-50 py-12 border-t">
          <div className="max-w-5xl mx-auto px-4">
            <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-center">Preventive Maintenance — FAQs</h2>
            <div className="grid md:grid-cols-2 gap-8 text-left">
              <div>
                <h3 className="font-semibold text-gray-900">How do I create a plan?</h3>
                <p className="text-gray-700 mb-4">Use the free generator on this page. Enter asset details and get a CMMS-ready plan in under 2 minutes.</p>
                <h3 className="font-semibold text-gray-900">Is it free?</h3>
                <p className="text-gray-700 mb-4">Yes. You can generate and download a plan for free here.</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Can I export to my CMMS?</h3>
                <p className="text-gray-700 mb-4">Yes. Export to Excel/CSV and import to your CMMS. Field mapping guidance included.</p>
                <h3 className="font-semibold text-gray-900">Who is ArcTecFox for?</h3>
                <p className="text-gray-700">Maintenance and reliability teams managing 50+ assets per site in regulated, asset-heavy industries.</p>
              </div>
            </div>
            <div className="text-center mt-6">
              <Link to="/faq" className="text-blue-600 font-semibold hover:underline">See the full FAQ →</Link>
            </div>
          </div>
        </section>

        {/* GENERATOR */}
        <section id="pm-planner-section" className="max-w-5xl mx-auto px-4 py-16">
          <h2 className="text-2xl sm:text-3xl font-bold mb-6">Free Preventive Maintenance Plan Generator</h2>

          {emailSent ? (
            /* Success Message - Blue Primary Theme */
            <div className="bg-white border-2 border-blue-500 rounded-lg p-12 text-center shadow-lg">
              <div className="mb-6">
                <svg className="w-20 h-20 text-blue-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
                </svg>
              </div>
              <h3 className="text-3xl font-bold text-gray-900 mb-4">Check Your Email!</h3>
              <p className="text-lg text-gray-700 mb-2">
                We've sent a confirmation link to:
              </p>
              <p className="text-xl font-semibold text-blue-600 mb-6">
                {submittedEmail}
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 text-left max-w-2xl mx-auto">
                <h4 className="font-semibold text-gray-900 mb-3">Next Steps:</h4>
                <ol className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="font-bold mr-2">1.</span>
                    <span>Check your inbox for an email from ArcTecFox</span>
                  </li>
                  <li className="flex items-start">
                    <span className="font-bold mr-2">2.</span>
                    <span>Click the "Confirm Email & Get Your PM Plan" button</span>
                  </li>
                  <li className="flex items-start">
                    <span className="font-bold mr-2">3.</span>
                    <span>We'll immediately email you the PDF with your custom PM plan</span>
                  </li>
                </ol>
              </div>
              <p className="text-sm text-gray-600 mb-8">
                Don't see it? Check your spam folder. The confirmation link expires in 24 hours.
              </p>
              <button
                onClick={() => {
                  setEmailSent(false);
                  setSubmittedEmail("");
                }}
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 shadow transition-colors"
              >
                <span>⚡</span> Generate Another Plan
              </button>
            </div>
          ) : (
            /* Original Form */
            <>
              <ProgressBar
                progress={completion}
                label={
                  assetName
                    ? `You're close — finalize the structured plan for "${assetName}".`
                    : `Answer a few fields to generate your structured baseline plan.`
                }
              />
              <PMPlannerOpen onChange={handlePlannerProgress} onGenerate={handlePlannerSubmit} disabled={submitting} />
            </>
          )}
        </section>

        {/* FINAL CTA */}
        <section className="bg-white py-10 border-t text-center">
          <div className="max-w-5xl mx-auto px-4">
            <h3 className="text-xl font-semibold mb-2">Plan, Prevent, Perform.</h3>
            <p className="text-gray-700 mb-6">Start with a structured baseline. Keep it effective with Continuous PM Optimization.</p>
            <button
              onClick={scrollToGenerator}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 shadow"
            >
              <span>⚡</span> Generate My Free PM Plan
            </button>
          </div>
        </section>

        {/* Structured Data (JSON-LD via dangerouslySetInnerHTML to avoid Vite normalization) */}
        <Helmet>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                mainEntity: [
                  {
                    "@type": "Question",
                    name: "How do I create a preventive maintenance plan?",
                    acceptedAnswer: {
                      "@type": "Answer",
                      text:
                        "Use the Free PM Plan Generator on the landing page. Enter asset type, usage hours, environment, and start date to receive a structured baseline with tasks, intervals, and schedule logic.",
                    },
                  },
                  {
                    "@type": "Question",
                    name: "Is it free?",
                    acceptedAnswer: {
                      "@type": "Answer",
                      text:
                        "Yes. You can generate and download a plan for free directly from the landing page.",
                    },
                  },
                  {
                    "@type": "Question",
                    name: "Can I export the PM plan to my CMMS?",
                    acceptedAnswer: {
                      "@type": "Answer",
                      text:
                        "Yes. Export to Excel/CSV and import into your CMMS. Field mapping guidance is provided.",
                    },
                  },
                  {
                    "@type": "Question",
                    name: "What is Continuous PM Optimization?",
                    acceptedAnswer: {
                      "@type": "Answer",
                      text:
                        "ArcTecFox's branded process to keep PM effective over time: quarterly reviews, lifecycle-aligned updates, and data-driven revisions.",
                    },
                  },
                  {
                    "@type": "Question",
                    name: "Which assets are supported?",
                    acceptedAnswer: {
                      "@type": "Answer",
                      text:
                        "HVAC, compressors, pumps, chillers, CNC, conveyors, motors, and custom entries for your assets under management.",
                    },
                  },
                ],
              }),
            }}
          />
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "HowTo",
                name: "How to create a preventive maintenance plan",
                step: [
                  { "@type": "HowToStep", name: "Choose asset type", text: "Select the equipment (HVAC, compressor, CNC, chiller, etc.)." },
                  { "@type": "HowToStep", name: "Enter usage & conditions", text: "Provide hours, environment, and criticality." },
                  { "@type": "HowToStep", name: "Generate schedule", text: "Click 'Generate My Free PM Plan' to create a CMMS-ready schedule." },
                  { "@type": "HowToStep", name: "Export", text: "Download Excel/CSV and import into your CMMS." }
                ],
              }),
            }}
          />
        </Helmet>

        {showLeadModal && (
          <LeadCaptureModal
            submitting={submitting}
            onClose={() => setShowLeadModal(false)}
            onLeadSubmit={handleLeadSubmit}
          />
        )}

        {showLoadingModal && (
          <ParentPlanLoadingModal
            isOpen={showLoadingModal}
            status={loadingStatus}
            progress={loadingProgress}
            onClose={() => setShowLoadingModal(false)}
          />
        )}

        <footer className="mt-12 border-t py-6 text-center text-sm text-gray-600">
          © {new Date().getFullYear()} ArcTecFox. Plan, Prevent, Perform.
        </footer>
      </div>

    </>
  );
}
