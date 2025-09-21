import React from "react";
import { Link } from "react-router-dom";
import SEO from "../components/SEO";
import { Helmet } from "react-helmet-async";

const QA = ({ q, a }) => (
  <div className="mb-6">
    <h3 className="font-semibold text-gray-900">{q}</h3>
    <p className="text-gray-700">{a}</p>
  </div>
);

export default function FAQ() {
  const faqs = [
    {
      q: "What is ArcTecFox?",
      a: "ArcTecFox generates structured, CMMS-ready preventive maintenance (PM) plans in under 2 minutes. Plan, Prevent, Perform — keep assets under management reliable and compliant."
    },
    {
      q: "How do I create a preventive maintenance plan?",
      a: "Use the Free PM Plan Generator on the home page. Enter asset type, usage hours, environment, and start date. You’ll receive a structured baseline with tasks, intervals, and schedule logic."
    },
    {
      q: "Is it free?",
      a: "Yes. You can generate and download a plan for free directly from the landing page."
    },
    {
      q: "Can I export and integrate with my CMMS?",
      a: "Yes. Export to Excel/CSV and import into your CMMS. We include mapping guidance. Native integrations are being expanded."
    },
    {
      q: "Which assets are supported?",
      a: "HVAC, compressors, pumps, chillers, CNC, conveyors, motors — plus custom entries to match your assets under management."
    },
    {
      q: "How long does it take?",
      a: "Under 2 minutes for most assets."
    },
    {
      q: "What is Continuous PM Optimization?",
      a: "Our branded process to keep PM effective over time: quarterly reviews, lifecycle-aligned updates, and data-driven revisions using standards, failure data, technician feedback, and audits."
    },
    {
      q: "Do you support multi-site portfolios?",
      a: "Yes. Mid-market to enterprise teams with 50+ assets per site use ArcTecFox to standardize a baseline and revise on a predictable cadence."
    },
    {
      q: "Who is ArcTecFox for?",
      a: "Maintenance managers, reliability engineers, and operations leaders in asset-heavy, regulated industries (healthcare, manufacturing, energy, transportation, oil & gas)."
    },
    {
      q: "Do you store my data?",
      a: "We store plan metadata and contact information to support revisions and improve recommendations. See our Privacy Policy for details."
    },
  ];

  return (
    <>
      <SEO
        title="Preventive Maintenance Plan FAQ | ArcTecFox"
        description="Straight answers on preventive maintenance planning, CMMS export, supported assets, and Continuous PM Optimization."
      />

      <div className="bg-white">
        <section className="max-w-4xl mx-auto px-4 py-14">
          <div className="mb-8">
            <Link to="/" className="text-blue-600 hover:underline">← Back to Home</Link>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-6">
            Preventive Maintenance — Frequently Asked Questions
          </h1>
          <p className="text-gray-700 mb-10">
            Clear, practical guidance from reliability engineers. Plan, Prevent, Perform.
          </p>

          <div className="divide-y">
            {faqs.map((f, i) => (
              <div key={i} className="py-6 first:pt-0">
                <QA q={f.q} a={f.a} />
              </div>
            ))}
          </div>

          <div className="mt-10 text-center">
            <Link
              to="/"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 shadow"
            >
              <span>⚡</span> Generate My Free PM Plan
            </Link>
          </div>
        </section>
      </div>

      {/* JSON-LD via dangerouslySetInnerHTML so Vite doesn't try to normalize it */}
      <Helmet>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FAQPage",
              mainEntity: faqs.map((f) => ({
                "@type": "Question",
                name: f.q,
                acceptedAnswer: { "@type": "Answer", text: f.a },
              })),
            }),
          }}
        />
      </Helmet>
    </>
  );
}
