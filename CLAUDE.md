# CLAUDE.md

ArcTecFox Mono - AI-powered Preventive Maintenance planning application.

## Tech Stack
- **Frontend**: React 18 + TypeScript, Vite, Tailwind CSS, Radix UI
- **Backend**: FastAPI (Python)
- **Database**: Supabase (auth, storage, RLS)
- **AI**: Google Gemini

## Development Commands
```bash
# Quick start (Codespaces)
/workspaces/ArcTecFox_Mono/start-dev.sh

# Manual start
cd apps/welcome/backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
npm run dev  # Frontend from root
```

## Core Database Schema
```sql
-- Assets (hierarchical)
parent_assets (id, name, site_id, critical_spare_parts, ...)
child_assets (id, name, parent_asset_id, plan_start_date, ...)

-- PM System
pm_plans (id, child_asset_id, site_id, status, ...)  -- child_asset_id = NULL for parent plans
pm_tasks (id, pm_plan_id, task_name, maintenance_interval, criticality, ...)
task_signoff (id, tech_id, task_id, due_date, comp_date, status, ...)

-- User Management
site_users (user_id, site_id, role_id)
invitations (id, email, site_id, token, expires_at, ...)
loaded_manuals (id, parent_asset_id, extracted_text, ...)
```

## Key Relationships
- PM plans link to **child assets only** (`pm_plans.child_asset_id`)
- Parent plans use `child_asset_id = NULL`
- Site access: `task_signoff → pm_tasks → pm_plans → child_assets → parent_assets → sites`
- Due dates: `child_assets.plan_start_date` + `pm_tasks.maintenance_interval`

## Authentication & Security
- **Supabase JWT tokens** for all API calls
- **RLS policies** enforce site-based data isolation
- All endpoints require `verify_supabase_token()`

## Environment Variables
```bash
# Frontend
VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_BACKEND_URL

# Backend  
SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, GEMINI_API_KEY
```

## CRITICAL - DO NOT MODIFY

### 1. Task View Query Pattern
```javascript
// MUST use exact nested join - DO NOT CHANGE
const { data } = await supabase
  .from('task_signoff')
  .select(`
    id, due_date, comp_date, status,
    pm_tasks!inner (
      id, task_name, criticality,
      pm_plans!inner (
        id, status, child_asset_id, site_id,
        child_assets!inner (id, name)
      )
    )
  `)
  .neq('status', 'deleted')
  .eq('pm_tasks.pm_plans.status', 'Current')
```

### 2. Calendar Layout (PERFECT)
- Fixed 980px width (7 columns × 140px)
- Navigation: `shrink-0` classes
- Month title: `w-[180px] shrink-0`
- Calendar cells: `w-[140px]`

### 3. RLS Policies - EXTREME CAUTION
```sql
-- ❌ NEVER create circular references
CREATE POLICY "bad" ON site_users USING (
  site_id IN (SELECT site_id FROM site_users WHERE user_id = auth.uid()) -- CIRCULAR!
);

-- ✅ Use simple patterns
CREATE POLICY "good" ON table USING (created_by = auth.uid());
```

### 4. Parsing Function (parseMaintenanceInterval)
Located in `apps/welcome/frontend/src/api.js` - converts AI intervals ("Monthly" → 1, "Every 3 months" → 3). MUST stay synchronized with backend `task_due_dates.py`.

### 5. AI Configuration - Centralized (DO NOT DUPLICATE)
**ALL** Google Gemini AI calls MUST use the centralized configuration in `apps/welcome/backend/config.py`:
```python
from config import get_gemini_model

# Use centralized config (applies defaults)
model = get_gemini_model()

# Override specific parameters as needed
model = get_gemini_model(temperature=0.7, response_mime_type="application/json")
```

**NEVER** create model instances directly with `genai.GenerativeModel()` or duplicate config values. To update the model globally, change `GEMINI_MODEL` in `config.py` only.

## Common Patterns
```javascript
// ✅ Correct Supabase patterns
.select('id,email,name')    // No spaces
.insert([{field: value}])   // Array insert

// ❌ Wrong patterns cause 406 errors
.select('id, email, name')  // Spaces
.insert({field: value})     // Object insert
```

## Key Features

### Parent Asset PM System
- **Creation**: `ManageAssets.jsx` → `ParentPlanLoadingModal` → AI generation
- **API**: `generateParentPlan()`, `createParentPMPlan()`, `updateParentAssetSpares()`
- **Backend**: `/api/generate-parent-plan` endpoint
- **Display**: Asset Insights dashboard shows parent tasks and spare parts

### PDF Text Extraction
- **Frontend**: `fileTextExtractor.js` handles PDF/text/images using PDF.js
- **Storage**: `loaded_manuals.extracted_text` stores manual content
- **Inheritance**: Child assets inherit parent's manual text for PM generation

### SEO Implementation
- **Pattern**: Import `SEO` component, wrap page with Fragment:
```javascript
return (
  <>
    <SEO 
      title="Page Title" 
      description="Page description (150-160 chars)"
      noindex={false}  // true for protected pages
    />
    <div>{/* content */}</div>
  </>
);
```

## File Storage
- Site-based: `sites/{site_id}/{filename}`
- Legacy: `{user_id}/{filename}` (backward compatibility)

## Development Rules
1. **Reuse existing functions** from `api.js`, `storageService.js`
2. **Follow exact query patterns**
3. **Test RLS changes in dev first**
4. **Check existing patterns before creating new ones**
5. **Prompt workflow**: All Gemini prompt reviews/updates must start with gemini-prompt-engineer agent for optimization, then ai-engineer agent implements the optimized prompts

## CURRENT ISSUES

### Toast Notification - Timestamp-based State Pattern (RESOLVED)
**Issue**: Toast notifications from `ParentPlanLoadingModal` appear on first "Generate PM Plan" click but not on subsequent clicks.

**Root Cause**: React's useEffect dependency optimization. When using a boolean state like `parentPlanSuccess`, React sees identical state transitions (false→true→false→true) and optimizes away subsequent useEffect executions, preventing the toast from appearing.

**Solution**: Use timestamp-based state instead of boolean. Each success generates a unique timestamp value using `Date.now()`, forcing useEffect to execute every time.

**Implementation** (ManageAssets.jsx):
```javascript
// Line 157: Use null instead of false
const [parentPlanSuccessTimestamp, setParentPlanSuccessTimestamp] = useState(null);

// Line 638: Set unique timestamp on success
setParentPlanSuccessTimestamp(Date.now());

// Line 2267: Convert to boolean for modal prop
success={!!parentPlanSuccessTimestamp}

// Lines 557, 2272: Reset to null
setParentPlanSuccessTimestamp(null);
```

**General Pattern**: Use timestamp-based state (`Date.now()`) whenever useEffect needs to respond to repeated events, not just state changes. This prevents React's dependency array optimization from skipping executions.