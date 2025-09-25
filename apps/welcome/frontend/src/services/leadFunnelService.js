// services/leadFunnelService.js
// Use the shared Supabase client from api.js to prevent multiple instances
import { supabase } from '../api';

// Coerce possible string fields to arrays
const toArray = (v) => {
  if (Array.isArray(v)) return v;
  if (v == null) return [];
  // split on newline if a long string, otherwise single-item array
  const s = String(v).trim();
  if (!s) return [];
  return s.includes("\n") ? s.split("\n").map(x => x.trim()).filter(Boolean) : [s];
};

export async function saveLeadAndPlan({ form, lead, tasks }) {
  // 1) create pm_leads
  const leadPayload = {
    org_name: lead.company || null,
    email: lead.email || null,
    asset_name: form.name || null,
    asset_type: form.category || null,
    usage_environment: form.environment || null,
    notes: form.additional_context || null,
    generated_plan: tasks ? tasks : null, // snapshot at lead level
  };

  const { data: leadRow, error: leadErr } = await supabase
    .from("pm_leads")
    .insert(leadPayload)
    .select()
    .single();

  if (leadErr) throw new Error(`Lead insert failed: ${leadErr.message}`);

  // 2) create pm_plans
  const planPayload = {
    lead_id: leadRow.id,
    plan_start_date: form.date_of_plan_start || null,
    asset_name: form.name || null,
    asset_model: form.model || null,
    serial_no: form.serial || null,
    eq_category: form.category || null,
    op_hours: form.hours ? Number(form.hours) : null,
    env_desc: form.environment || null,
    additional_context: form.additional_context || null,
    status: "draft",
    version: 1,
  };

  const { data: planRow, error: planErr } = await supabase
    .from("pm_plans")
    .insert(planPayload)
    .select()
    .single();

  if (planErr) throw new Error(`Plan insert failed: ${planErr.message}`);

  // 3) create pm_plan_versions (v1)
  const versionPayload = {
    pm_plan_id: planRow.id,
    version_number: 1,
    input_snapshot: form,
    generated_tasks: tasks || [],
    source: "manual" // or "ai"
  };

  const { data: versionRow, error: versionErr } = await supabase
    .from("pm_plan_versions")
    .insert(versionPayload)
    .select()
    .single();

  if (versionErr) throw new Error(`Plan version insert failed: ${versionErr.message}`);

  // 4) create pm_tasks (bulk)
  if (Array.isArray(tasks) && tasks.length > 0) {
    // Helper function to convert arrays to comma-separated text for text columns
    const arrayToText = (value) => {
      if (Array.isArray(value)) {
        return value.filter(v => v && v !== 'Not applicable').join(', ');
      }
      return value || null;
    };

    const tasksPayload = tasks.map((t) => ({
      pm_plan_id: planRow.id,
      task_name: t.task_name || t.name || "Task",
      maintenance_interval: t.maintenance_interval || t.interval || null,
      instructions: toArray(t.instructions), // Keep as array for jsonb[] column
      reason: t.reason || null,
      engineering_rationale: t.engineering_rationale || null,
      safety_precautions: arrayToText(t.safety_precautions), // Convert array to text
      common_failures_prevented: arrayToText(t.common_failures_prevented), // Convert array to text
      usage_insights: t.usage_insights || null,
      scheduled_dates: toArray(t.scheduled_dates),
      est_minutes: t.estimated_time_minutes || t.est_minutes || null,
      tools_needed: arrayToText(t.tools_needed), // Convert array to text
      no_techs_needed: t.number_of_technicians || (t.no_techs_needed ? Number(t.no_techs_needed) : null),
      consumables: arrayToText(t.consumables), // Convert array to text
      status: "draft",
      criticality: t.criticality_rating || t.criticality || null
    }));

    const { error: tasksErr } = await supabase.from("pm_tasks").insert(tasksPayload);
    if (tasksErr) throw new Error(`Task inserts failed: ${tasksErr.message}`);
  }

  return { lead: leadRow, plan: planRow, version: versionRow };
}
