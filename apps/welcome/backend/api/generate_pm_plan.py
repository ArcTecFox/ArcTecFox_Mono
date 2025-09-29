# generate_pm_plan.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import logging
import os
import json
from typing import Optional, Any, Dict

router = APIRouter()
logger = logging.getLogger("main")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ============
# Input model
# ============
class PMPlanInput(BaseModel):
    name: str
    model: str
    serial: str
    category: str
    hours: str            # Cumulative runtime hours since installation (calculated value)
    frequency: str
    criticality: str
    additional_context: str  # Any special notes or focus points for the plan
    parent_asset: Optional[str] = None   # Parent asset name
    child_asset: Optional[str] = None    # Child asset name
    site_location: Optional[str] = None  # e.g., "Dallas Plant, Line 3"
    environment: Optional[str] = None    # e.g., "High humidity, corrosive, outdoor, Class I Div 2"
    parent_asset_id: Optional[str] = None  # Parent asset ID for hours calculation
    child_asset_id: Optional[str] = None   # Child asset ID for hours calculation


# =================
# Prompt generator
# =================
def generate_prompt(data: PMPlanInput) -> str:
    today = datetime.utcnow().date().isoformat()
    parent_asset = data.parent_asset if data.parent_asset else "Not applicable"
    child_asset = data.child_asset if data.child_asset else "Not applicable"
    site_location = data.site_location if data.site_location else "Not applicable"
    environment = data.environment if data.environment else "Not applicable"
    hours = data.hours if data.hours else "Not applicable"
    frequency = data.frequency if data.frequency else "Not applicable"
    criticality = data.criticality if data.criticality else "Medium"
    addl = data.additional_context if data.additional_context else "Not applicable"

    return f"""
ROLE & SCOPE
You are an expert in enterprise asset management, industrial machinery, and preventive maintenance planning. 
You have deep knowledge of rotating equipment, mechanical systems, electrical systems, and control systems across 
multiple industries. You generate authoritative, standard-compliant preventive maintenance plans for child assets 
(components), drawing from OEM manuals, ISO/ASTM/API standards, and trusted supplier guidance (e.g., SKF, Mobil, Shell).
Produce a child-asset/component-level PM plan for the specified child asset (component scope only).


UNIVERSAL CONTEXT (inherits unless overridden at task level)
- Parent Asset: {parent_asset}
- Child Asset: {child_asset}
- Site Location: {site_location}
- Environment: {environment}
- Cumulative Runtime Hours: {hours} (calculated as weeks since installation × parent asset's weekly operating hours)
- PM Frequency: {frequency}
- Criticality: {criticality}
- Additional Context: {addl}
- Plan Start Date: {today}

IMPORTANT - Runtime Hours Context:
The provided runtime hours represent the total accumulated operating hours since the child asset's installation date. This value is calculated by multiplying the number of weeks between the installation date and today by the parent asset's weekly operating hours. Use this cumulative runtime to inform maintenance intervals based on actual equipment usage rather than calendar time alone. Higher cumulative hours may require more frequent maintenance intervals to prevent wear-related failures.

POLICIES (MANDATORY)
- If the system has manufacturer manual content available, treat it as primary. Extract concrete instructions/intervals/specs/lubricants/part numbers and cite exact sections/pages in "citations".
- CRITICAL RULE - Manual Text Usage: When manual content is provided:
  1. You MUST extract and include specific maintenance procedures, part numbers, torque specifications, intervals, and step-by-step instructions DIRECTLY from the provided manual text
  2. You are STRICTLY FORBIDDEN from using phrases like "refer to manual", "consult documentation", "see user manual", or ANY similar reference phrases
  3. Each maintenance task MUST incorporate the actual details found in the manual text
  4. Include exact specifications: part numbers, torque values, clearances, pressures, fluid types, quantities
  5. Include step-by-step procedures as found in the manual
  6. Self-check: Before outputting any task, verify you have NOT used any phrase that directs users to external documentation when manual text was provided. Instead, ensure you've included the actual information from the manual.
- If no manual content is available, use recognized standards/suppliers (ISO/ASTM/API; SKF/Mobil/Shell). Cite them. Never write “refer to the manual”; always provide actual values/steps.
- Do not include calendar dates anywhere; use numeric intervals in **weeks** only.


- CRITICAL: Do NOT include "Visual Inspection" or "Monthly cleaning" tasks at the child asset level as these are handled at the parent asset level.
- Exclude any routine cleaning or visual-only inspections unless the OEM manual explicitly prescribes them for this specific component (not general system) or a standard/supplier requires them. If included, cite the exact source.
- Focus on technical, measurable tasks specific to the child asset (lubrication, torque, calibration, functional checks, replacements, adjustments, monitoring, safety interlocks).


DEDUPLICATION & INHERITANCE
- Treat Site Location, Environment, Operating Hours, and Criticality as universal context. Do NOT repeat them in every field; only note deviations in "context_overrides".
- Keep language concise. Avoid redundant phrasing across tasks.

DATA TYPES & UNITS
- maintenance_interval: **weeks as a number ONLY**. Mapping:
  Daily ≈ 0.143, Weekly = 1, Biweekly = 2, Monthly ≈ 4, Quarterly ≈ 13, Yearly ≈ 52. Use fractional weeks as needed.
- estimated_time_minutes, number_of_technicians: integers.
- Use "Not applicable" for any field where nothing applies. Arrays must contain at least one item (e.g., ["Not applicable"]) when otherwise empty.
- Safety steps must precede any action that could expose energy. If LOTO applies, include it as the first step.

CHILD-ASSET SCOPE NOTES
- Include lubrication tasks when applicable; identify grease points/zones if known. Provide specific product/type/quantity when available (prefer OEM), otherwise standards/suppliers with citations.

TASK NAMING CONVENTION
- task_name = "{child_asset} – {{Action}} – {{Area/Subsystem}}" (no marketing fluff).

HALLUCINATION GUARDRAILS
- Never fabricate part numbers or brand-specific specs. If not known credibly, choose a conservative, widely accepted default and record rationale in "assumptions".
- If any universal field is unknown, proceed with best practices and add a brief assumption.

OUTPUT SECTION
"maintenance_plan": child-asset tasks ONLY.

REQUIRED FIELDS for each task (never omit; use "Not applicable" where needed):
- "parent_asset", "child_asset", "task_name", "maintenance_interval",
- "instructions" (array of steps),
- "reason", "engineering_rationale",
- "safety_precautions" (array),
- "common_failures_prevented" (array),
- "usage_insights",
- "tools_needed" (array),
- "number_of_technicians", "estimated_time_minutes",
- "consumables" (array),
- "risk_assessment",
- "criticality_rating" ("High"|"Medium"|"Low"),
- "comments",
- "assumptions" (array),
- "citations" (array),
- "inherits_parent_context" (bool),
- "context_overrides" (object with allowed keys: site_location, environment, operating_hours, criticality; empty if none)

FEW-SHOT EXAMPLE (ABBREVIATED; 1 task)
{{
  "parent_asset": "{parent_asset}",
  "child_asset": "{child_asset}",
  "task_name": "{child_asset} – Bearing Lubrication – Drive End",
  "maintenance_interval": 4,
  "instructions": [
    "Lock out/tag out per site policy",
    "Clean grease fitting and surrounding area",
    "Apply 2–3 shots of NLGI #2 lithium complex grease (per OEM spec) to the drive-end bearing",
    "Rotate shaft manually to distribute grease",
    "Wipe excess and re-install fitting cap"
  ],
  "reason": "Maintain adequate film and prevent bearing wear due to lubricant depletion",
  "engineering_rationale": "Approx. monthly (4 weeks) interval aligned to continuous operation in {environment}; adjust if temperature trending indicates",
  "safety_precautions": ["PPE per site policy", "LOTO before contact with rotating equipment"],
  "common_failures_prevented": ["Bearing overheating", "Premature wear", "Seizure"],
  "usage_insights": "With {hours} cumulative runtime hours since installation, consider trending vibration/temperature to optimize interval based on actual usage patterns",
  "tools_needed": ["Grease gun with zerk coupler", "Clean lint-free wipes"],
  "number_of_technicians": 1,
  "estimated_time_minutes": 15,
  "consumables": ["NLGI #2 lithium complex grease (e.g., Mobil XHP 222)"],
  "risk_assessment": "Low risk when LOTO applied; risk increases if contamination occurs",
  "criticality_rating": "Medium",
  "comments": "Not applicable",
  "assumptions": ["OEM spec calls for NLGI #2; quantity verified on nameplate/manual"],
  "citations": ["ISO 17359 – Condition monitoring", "SKF Grease Guide"],
  "inherits_parent_context": true,
  "context_overrides": {{}}
}}

FINAL OUTPUT REQUIREMENTS
- Return ONE JSON object only, no extra text.
- Begin your output immediately with:
{{
  "maintenance_plan": [

SCHEMA REMINDER
{{
  "maintenance_plan": [ {{task1}}, {{task2}}, ... ]
}}
"""


# =====================
# Validation utilities
# =====================
def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _validate_plan_structure(plan_json: Dict[str, Any]) -> None:
    """
    Validate required structure and fields for the AI output.
    Raises HTTPException(422) with details on failure.
    """
    if not isinstance(plan_json, dict) or "maintenance_plan" not in plan_json:
        raise HTTPException(status_code=422, detail="Output must be a JSON object with key 'maintenance_plan'.")

    tasks = plan_json.get("maintenance_plan")
    if not isinstance(tasks, list) or len(tasks) == 0:
        raise HTTPException(status_code=422, detail="'maintenance_plan' must be a non-empty array of task objects.")

    errors = []
    for idx, task in enumerate(tasks):
        path = f"maintenance_plan[{idx}]"
        if not isinstance(task, dict):
            errors.append(f"{path} is not an object")
            continue

        # Required keys presence (even if "Not applicable")
        required_keys = [
            "parent_asset", "child_asset", "task_name", "maintenance_interval", "instructions",
            "reason", "engineering_rationale", "safety_precautions", "common_failures_prevented",
            "usage_insights", "tools_needed", "number_of_technicians", "estimated_time_minutes",
            "consumables", "risk_assessment", "criticality_rating", "comments", "assumptions",
            "citations", "inherits_parent_context", "context_overrides"
        ]
        for key in required_keys:
            if key not in task:
                errors.append(f"{path}.{key} is missing")

        # Numeric validations
        if "maintenance_interval" in task and not _is_number(task.get("maintenance_interval")):
            errors.append(f"{path}.maintenance_interval must be numeric (weeks)")
        if "estimated_time_minutes" in task and not _is_number(task.get("estimated_time_minutes")):
            errors.append(f"{path}.estimated_time_minutes must be numeric (minutes)")

        # Enum validation for criticality_rating
        if "criticality_rating" in task:
            val = task.get("criticality_rating")
            if not isinstance(val, str) or val.strip().title() not in {"High", "Medium", "Low"}:
                errors.append(f"{path}.criticality_rating must be one of High, Medium, Low")

        # Type expectations
        if "inherits_parent_context" in task and not isinstance(task.get("inherits_parent_context"), bool):
            errors.append(f"{path}.inherits_parent_context must be boolean")
        if "context_overrides" in task and not isinstance(task.get("context_overrides"), dict):
            errors.append(f"{path}.context_overrides must be an object (dict)")

        # Disallow deprecated or off-spec fields
        if "scheduled_dates" in task:
            errors.append(f"{path}.scheduled_dates must NOT be included; use maintenance_interval in weeks instead")

    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})


# ==========
# Endpoint
# ==========
@router.post("/api/generate-ai-plan")
async def generate_ai_plan(input: PMPlanInput, request: Request):
    logger.info(f"🚀 Received AI plan request: {input.name}")

    # Calculate runtime hours if parent_asset and child_asset data is available
    calculated_hours = input.hours

    if hasattr(input, 'parent_asset_id') and hasattr(input, 'child_asset_id') and input.parent_asset_id and input.child_asset_id:
        try:
            from database import get_service_supabase_client
            service_client = get_service_supabase_client()

            # Fetch parent asset's hours_run_per_week
            parent_response = service_client.table('parent_assets').select('hours_run_per_week').eq('id', input.parent_asset_id).limit(1).execute()

            if parent_response.data and len(parent_response.data) > 0:
                hours_run_per_week = parent_response.data[0].get('hours_run_per_week')

                if hours_run_per_week:
                    # Fetch child asset's install date (plan_start_date)
                    child_response = service_client.table('child_assets').select('plan_start_date').eq('id', input.child_asset_id).limit(1).execute()

                    if child_response.data and len(child_response.data) > 0:
                        install_date = child_response.data[0].get('plan_start_date')

                        if install_date:
                            from datetime import datetime, date

                            # Parse install date
                            if isinstance(install_date, str):
                                install_date = datetime.fromisoformat(install_date.replace('Z', '+00:00')).date()
                            elif isinstance(install_date, datetime):
                                install_date = install_date.date()

                            # Calculate weeks since install and total hours
                            current_date = date.today()
                            weeks_since_install = (current_date - install_date).days / 7
                            total_hours = max(0, int(weeks_since_install * hours_run_per_week))
                            calculated_hours = str(total_hours)

                            logger.info(f"📊 Runtime hours calculated: {calculated_hours} hours (weeks: {weeks_since_install:.1f}, weekly_hours: {hours_run_per_week})")
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate runtime hours: {e}")

    # Create modified input with calculated hours
    modified_input = PMPlanInput(
        name=input.name,
        model=input.model,
        serial=input.serial,
        category=input.category,
        hours=calculated_hours,
        frequency=input.frequency,
        criticality=input.criticality,
        additional_context=input.additional_context,
        parent_asset=input.parent_asset,
        child_asset=input.child_asset,
        site_location=input.site_location,
        environment=input.environment,
        parent_asset_id=getattr(input, 'parent_asset_id', None),
        child_asset_id=getattr(input, 'child_asset_id', None)
    )

    prompt = generate_prompt(modified_input)

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,               # more deterministic for schema output
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
            system_instruction="Always return pure JSON, no markdown, no prose outside the JSON."
        )

        full_prompt = (
            "You are an expert in preventive maintenance planning. "
            "Always return pure JSON without any markdown formatting.\n\n" + prompt
        )

        response = model.generate_content(full_prompt)
        ai_output = (response.text or "").replace("```json", "").replace("```", "").strip()

        # Parse & validate
        try:
            plan_json = json.loads(ai_output)
        except json.JSONDecodeError:
            logger.error("AI output was not valid JSON")
            logger.error(f"Raw content (first 600 chars): {ai_output[:600]}...")
            raise HTTPException(status_code=422, detail="Model did not return valid JSON.")
        _validate_plan_structure(plan_json)

        logger.info("✅ AI plan generated and validated successfully")
        # Return in the format expected by the frontend (AIPlanResponse)
        maintenance_tasks = plan_json.get("maintenance_plan", [])
        return {"success": True, "data": maintenance_tasks}

    except Exception as e:
        logger.error(f"🧠 Gemini error: {e}")
        raise HTTPException(status_code=500, detail="Gemini API error.")
