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

## CURRENT WORK IN PROGRESS

### Supabase Authentication Testing - Request Access Flow

**Purpose**: Testing standalone Supabase authentication for new user onboarding (separate from existing invitation system).

#### Implementation Status: ✅ Complete

**What's Been Implemented:**

1. **Backend Changes** (`apps/welcome/backend/api/access_requests.py`):
   - ✅ Made `lead_id` optional (line 21) - allows testing without PM plan dependency
   - ✅ Added comprehensive logging with `[RequestAccess]` and `[ApproveAccess]` prefixes
   - ✅ Logs track: email submission, Supabase user creation, invite email sending
   - ✅ Full exception logging for debugging Supabase issues

2. **Frontend Components**:
   - ✅ Created `RequestAccessModal.jsx` - email input modal with "Request Access" and "Cancel" buttons
   - ✅ Updated `UserStatusBar.jsx` - added blue "Request Access" button next to white "Sign in" button
   - ✅ Hardcoded "Test User" for full_name (testing only)
   - ✅ Enhanced console logging for frontend debugging

3. **Email Configuration**:
   - ✅ Resend API key added to `.env` (for admin notifications to support@arctecfox.ai)
   - ✅ arctecfox.ai domain verified with Resend
   - ✅ Supabase handles user invite emails (password setup links)

#### Current Testing Status: 🧪 In Progress

**Completed:**
- ✅ Request Access button visible on landing page
- ✅ Modal opens and accepts email input
- ✅ Backend successfully creates access request in database
- ✅ Fixed duplicate email constraint issue (database allows only one request per email)
- ✅ Resend configuration complete (admin notifications ready)

**Next Steps:**
1. Restart backend server to load RESEND_KEY environment variable
2. Submit new access request with different email (e.g., `willisreed17+test2@outlook.com`)
3. Verify Resend admin notification sent to support@arctecfox.ai
4. Login as SuperAdmin → Approve access request
5. Check backend logs for Supabase user creation and invite email
6. Check user email for Supabase password setup link
7. Complete password setup and test login

#### Known Issues:

**Database Constraint:**
- `access_requests` table has unique constraint on `email` column
- Code currently only checks for "pending" status (line 144)
- Database blocks ALL duplicate emails (pending, approved, rejected)
- **Recommended fix**: Update duplicate check to handle all statuses with better error messages

**For Testing:**
- Use email aliases for multiple tests: `email+test1@domain.com`, `email+test2@domain.com`
- Or manually delete old access_request records from Supabase dashboard

#### File Locations:
- Backend API: `apps/welcome/backend/api/access_requests.py`
- Frontend Modal: `apps/welcome/frontend/src/components/RequestAccessModal.jsx`
- User Status Bar: `apps/welcome/frontend/src/components/UserStatusBar.jsx`
- Environment: `apps/welcome/backend/.env` (contains RESEND_KEY)



## PROPOSED IMPROVEMENTS

### Multi-Company User Management Redesign

**Current Limitation**: Users cannot be added to multiple companies. A user authenticated to Company A cannot be added to Company B sites due to company scoping validation in `add_existing_user.py` (lines 106-149).

**Proposed Solution**: Follow B2B SaaS best practices (Slack, GitHub, Asana pattern)

#### Core Principle: Users are Global, Access is Scoped
- Users exist independently (one email = one account)
- Access is granted per site via `site_users` table
- Roles are assigned per site
- RLS policies enforce data isolation

#### Simplified User Management Workflow

**For Site Admins - Single "Add User" Modal:**

```
1. Click [+ Add User] button
2. Enter email address
3. System auto-detects:
   - ✓ Existing user → Shows current company/site memberships → [Add to This Site]
   - ○ New user → Shows "will send invitation" → [Send Invitation]
4. Select role (Viewer, User, Editor, Admin)
5. Submit → Done (instant for existing, email for new)
```

**Key Changes Required:**

1. **Backend** (`apps/welcome/backend/api/add_existing_user.py`):
   ```python
   # REMOVE company restriction validation (lines 106-149)
   # Allow users to be added to any company
   # RLS policies still enforce they can only see data they have access to
   ```

2. **Frontend** (Add to `CompanyManagement.jsx` or create `SiteUserManagement.jsx`):
   - Smart email search with real-time user lookup
   - Show existing user's current memberships
   - Single modal handles both existing and new users
   - Inline role editing for existing site users

3. **No Schema Changes**: Existing `site_users` table already supports many-to-many relationship between users and sites

#### Benefits
- ✅ Supports contractors, consultants, multi-site employees
- ✅ Minimal code changes (remove 1 validation, add 1 UI component)
- ✅ Familiar pattern (matches industry standards)
- ✅ Maintains security via existing RLS policies
- ✅ ~3 hours implementation time

#### User Flows

**Flow 1: Add Existing User (Cross-Company)**
```
Site Admin → [+ Add User] → Types "john@acme.com" →
System finds: ✓ User exists (currently at Company A) →
Admin selects role: Editor → [Add to Site] → Done ✓ (instant access)
```

**Flow 2: Invite New User**
```
Site Admin → [+ Add User] → Types "newperson@example.com" →
System shows: ○ New user (will send invitation) →
Admin selects role: User → [Send Invitation] →
Email sent ✉ (7-day link) → User clicks link → Auto-added to site
```

#### Implementation Plan
1. **Phase 1** (15 min): Remove company validation in `add_existing_user.py`
2. **Phase 2** (2 hours): Build unified user management UI with smart email search
3. **Phase 3** (1 hour): Add real-time user search functionality

**Status**: Proposed, awaiting implementation approval

