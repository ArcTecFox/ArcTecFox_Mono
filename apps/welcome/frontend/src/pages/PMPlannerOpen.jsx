import React, { useEffect, useMemo, useState } from "react";

export default function PMPlannerOpen({ onGenerate, onChange, resetTrigger }) {
  const initialFormData = {
    name: "",
    model: "",
    serial: "",
    category: "",
    hours: "",
    additional_context: "",
    environment: "",
    date_of_plan_start: "",
  };
  
  const [formData, setFormData] = useState(initialFormData);
  const [submitting, setSubmitting] = useState(false);

  // Reset form when resetTrigger changes
  useEffect(() => {
    if (resetTrigger) {
      setFormData(initialFormData);
    }
  }, [resetTrigger]);

  // notify parent for progress bar
  useEffect(() => {
    onChange?.(formData);
  }, [formData, onChange]);

  const fieldKeys = useMemo(
    () => [
      "name",
      "model",
      "serial",
      "category",
      "hours",
      "additional_context",
      "environment",
      "date_of_plan_start",
    ],
    []
  );

  const filledCount = fieldKeys.filter(
    (k) => formData[k] && String(formData[k]).trim() !== ""
  ).length;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      onGenerate?.(formData);
    } catch (err) {
      console.error("Generate plan failed", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 bg-white p-6 rounded-lg shadow-md max-w-3xl mx-auto"
      aria-label="Free Preventive Maintenance Plan Generator"
    >
      <h2 className="text-2xl font-bold text-gray-800 mb-1">
        Generate Your Free Preventive Maintenance Plan
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        AI-powered generator creates a CMMS-ready preventive maintenance schedule based on your inputs.
        No spreadsheets. ~2 minutes.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Asset / Equipment */}
        <label className="sr-only" htmlFor="name">Asset or Equipment Name</label>
        <input
          id="name"
          type="text"
          name="name"
          placeholder="Asset or Equipment Name (e.g., Air Compressor, HVAC, CNC)"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.name}
          onChange={handleChange}
          required
        />

        {/* Model */}
        <label className="sr-only" htmlFor="model">Model</label>
        <input
          id="model"
          type="text"
          name="model"
          placeholder="Model (for maintenance schedule specificity)"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.model}
          onChange={handleChange}
        />

        {/* Serial */}
        <label className="sr-only" htmlFor="serial">Serial Number</label>
        <input
          id="serial"
          type="text"
          name="serial"
          placeholder="Serial Number (optional)"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.serial}
          onChange={handleChange}
        />

        {/* Category */}
        <label className="sr-only" htmlFor="category">Asset Category</label>
        <input
          id="category"
          type="text"
          name="category"
          placeholder="Asset Category (HVAC, Pump, Compressor, CNC, Chiller)"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.category}
          onChange={handleChange}
          required
        />

        {/* Hours */}
        <label className="sr-only" htmlFor="hours">Operating Hours per Month</label>
        <input
          id="hours"
          type="number"
          name="hours"
          placeholder="Operating Hours (per month) — helps set PM intervals"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.hours}
          onChange={handleChange}
          min="0"
        />

        {/* Start Date */}
        <label className="sr-only" htmlFor="date_of_plan_start">Plan Start Date</label>
        <input
          id="date_of_plan_start"
          type="date"
          name="date_of_plan_start"
          placeholder="Plan Start Date (when to begin your PM schedule)"
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          value={formData.date_of_plan_start}
          onChange={handleChange}
        />
      </div>

      {/* Additional Context */}
      <label className="sr-only" htmlFor="additional_context">Additional Context</label>
      <textarea
        id="additional_context"
        name="additional_context"
        placeholder="Additional Context (e.g., critical system, vibration, failures, OEM guidance)"
        className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        value={formData.additional_context}
        onChange={handleChange}
        rows={3}
      />

      {/* Environment */}
      <label className="sr-only" htmlFor="environment">Operating Environment</label>
      <textarea
        id="environment"
        name="environment"
        placeholder="Operating Environment (e.g., high humidity, dusty, clean room)"
        className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        value={formData.environment}
        onChange={handleChange}
        rows={3}
      />

      <div className="flex items-center justify-between">
        <div
          className={`text-sm ${filledCount >= 2 ? "text-blue-600" : "text-gray-500"} transition-colors`}
          aria-live="polite"
        >
          {filledCount} / {fieldKeys.length} fields completed
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          disabled={submitting}
          aria-label="Generate My Free Preventive Maintenance Plan"
        >
          {submitting ? "Generating..." : "Generate My Free PM Plan"}
        </button>
      </div>
    </form>
  );
}
