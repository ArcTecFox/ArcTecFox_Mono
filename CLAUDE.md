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

### User Management Page Redesign

**Goal**: Redesign the User Management page (`apps/welcome/frontend/src/pages/UserManagement.jsx`) to support different admin capabilities.

#### Requested Capabilities:
- **Company Admin**: Add users (already assigned to their company) to any site under that company
- **Site Admin**: Assign users (who exist in the system) to any company, and assign users (linked to a company) to a site under that company

#### Current Implementation:
- **Site-centric workflow**: Admin selects a site first, then manages users within that site
- **Two modes for adding users**:
  - "Add Existing User" - Search for users already in the same company
  - "Send Invitation" - Email invitation to new users
- **Permission-based access**:
  - Super Admin (`super_admin` role + `users.site_admin=true`): Sees all sites
  - Company Admin (`company_admin` role): Sees only sites they're assigned to
- **Current roles in DB**: `super_admin`, `company_admin`, `user`

#### Questions Awaiting Answers:

**1. Role Hierarchy Clarification**
Is "Site Admin" the same as `super_admin`? Or is this a new role between super_admin and company_admin?
- Current roles in DB: `super_admin`, `company_admin`, `user`
- Description implies Site Admin has MORE power than Company Admin (can assign to "any company")

**Answer**: _[PENDING]_

**2. Cross-Company Assignment**
Site Admin should "assign users who exist in the system to any company." Does this mean:
- Create new company-user relationships for ANY company in the system?
- Or only for companies they are associated with?

**Answer**: _[PENDING]_

**3. Intended Permission Hierarchy**
What is the intended hierarchy?
- `Super Admin` → Full system access
- `Site Admin` → ? (Description says cross-company, which seems very high-level)
- `Company Admin` → Manage sites/users within their company only
- `User` → Basic access

**Answer**: _[PENDING]_

**4. UI Expectations**
Should different admin types see different interfaces?
- Separate tabs/sections for "Manage Company Users" vs "Manage Site Users"?
- Or one unified view with different capabilities based on role?

**Answer**: _[PENDING]_

**5. Specific Workflows Needed**
Example scenarios needed:
- **Company Admin scenario**: "I want to add John (already in my company) to the Production site"
- **Site Admin scenario**: "I want to add Jane (exists in system) to Acme Corp, then add her to their Main site"

**Answer**: _[PENDING]_

**6. Current vs Desired State**
Is the `users.site_admin` boolean field intended to represent the "Site Admin" role being described, or is this something different?

**Answer**: _[PENDING]_

#### Next Steps:
Once questions are answered, pass context to UI/UX agent (`.claude/agents/design/`) to design revised page.

---

### Free PM Plan - Email Confirmation Flow

**Status**: ✅ Implementation Complete | ⚠️ Testing In Progress

**Goal**: Replace auto-download of PDF/Excel files with email confirmation workflow for free PM plan generation.

#### Implementation Summary (Completed)

**Database Changes:**
- Added columns to `pm_leads` table:
  - `confirmation_token` (VARCHAR 255, unique) - Secure token for email confirmation
  - `token_created_at`, `token_expires_at` (TIMESTAMPTZ) - 24-hour expiration tracking
  - `email_confirmed` (BOOLEAN) - Confirmation status
  - `email_confirmed_at` (TIMESTAMPTZ) - When user confirmed
  - `confirmed_from_ip` (VARCHAR 45) - Security tracking
  - `confirmation_email_sent_at`, `delivery_email_sent_at` (TIMESTAMPTZ) - Email tracking
  - `pdf_generated`, `pdf_generation_failed` (BOOLEAN) - PDF status
  - `status` (VARCHAR 20: 'pending'/'confirmed'/'expired'/'failed') - Overall status
  - `failure_reason` (TEXT) - Error tracking
  - `confirmation_attempts` (INTEGER) - Analytics
  - `company_name` (VARCHAR 255) - Dedicated company column

**Backend Changes:**
- **New File**: `api/email_confirmations.py`
  - `send_confirmation_email()` - Sends confirmation link (24hr expiration)
  - `send_delivery_email()` - Sends PDF after confirmation
  - `send_plan_generated_notification()` - Notifies support after confirmation
- **Modified**: `main.py`
  - `/api/lead-capture` - Now creates token, sends confirmation email (no PDF)
  - `/api/confirm-email/{token}` - New endpoint: validates token, generates PDF, sends email, redirects to frontend

**Frontend Changes:**
- **New File**: `pages/ConfirmEmail.jsx` - Email confirmation landing page (loading/success/error/already-confirmed states)
- **Modified**: `pages/Home.jsx` - Removed auto-downloads, shows "Check Your Email!" toast
- **Modified**: `App.jsx` - Added `/confirm-email` route

**Key Changes:**
- ❌ Excel export removed entirely
- ❌ PDF auto-download removed
- ✅ Email confirmation required before receiving PDF
- ✅ Support notifications sent AFTER confirmation (not before)
- ✅ Access request notifications sent AFTER confirmation
- ✅ One confirmed plan per email enforced (can retry if expired)

#### Testing Status

**✅ Completed Tests:**
1. Backend endpoint modification - No datetime scoping errors
2. Token generation and storage - Working correctly
3. Email sent with confirmation link - Emails being sent

**⚠️ In Progress:**
1. **Email Confirmation Link Testing**
   - **Current Issue**: Link uses `http://localhost:8000/api/confirm-email/{token}` which doesn't work when clicked from email
   - **Root Cause**: In Codespaces, localhost is not accessible from external email clients
   - **Solution Required**: Update `BACKEND_URL` environment variable to use Codespaces forwarded URL

**🔧 Configuration Required:**

**Backend `.env`** (`/workspaces/ArcTecFox_Mono/apps/welcome/backend/.env`):
```bash
# Replace localhost with Codespaces URL
BACKEND_URL=https://[your-codespace-name]-8000.app.github.dev
FRONTEND_URL=https://[your-codespace-name]-3000.app.github.dev  # or production URL
RESEND_API_KEY=re_xxxxx  # Already configured
```

**Frontend `.env`** (`/workspaces/ArcTecFox_Mono/apps/welcome/frontend/.env`):
```bash
VITE_BACKEND_URL=https://[your-codespace-name]-8000.app.github.dev
```

**How to Get Codespaces URLs:**
- Open VS Code PORTS tab (bottom panel)
- Port 8000 → Right-click → Copy "Forwarded Address" → Use for BACKEND_URL
- Port 3000 → Right-click → Copy "Forwarded Address" → Use for FRONTEND_URL
- **IMPORTANT**: Set port visibility to "Public" for both ports

**📋 Remaining Testing Checklist:**

1. **Happy Path:**
   - [ ] Generate free PM plan with valid email
   - [ ] Verify "Check Your Email!" toast appears
   - [ ] Check email inbox for confirmation email
   - [ ] Click "Confirm Email & Get Your PM Plan" button
   - [ ] Verify redirect to `/confirm-email?status=success`
   - [ ] Verify "Email Confirmed!" message displays
   - [ ] Check email inbox for delivery email with PDF attachment
   - [ ] Verify PDF attachment opens correctly
   - [ ] Check `support@arctecfox.co` receives:
     - Plan confirmation notification
     - Access request notification (if "Request Access" was checked)

2. **Error Cases:**
   - [ ] Expired token (24+ hours) → Shows "expired" error with "Generate New Plan" button
   - [ ] Already confirmed → Shows "already confirmed" message
   - [ ] Invalid token → Shows "invalid" error
   - [ ] Duplicate email → Blocks with error message

3. **Email Quality:**
   - [ ] Emails don't go to spam folder
   - [ ] Email formatting renders correctly in Gmail/Outlook/Apple Mail
   - [ ] Mobile email clients display correctly
   - [ ] PDF attachment is properly attached and downloadable

4. **Analytics Queries:**
```sql
-- Confirmation rate (last 30 days)
SELECT
    COUNT(*) FILTER (WHERE email_confirmed = true) * 100.0 / COUNT(*) as rate
FROM pm_leads
WHERE submitted_at > NOW() - INTERVAL '30 days';

-- Average time to confirm
SELECT
    AVG(EXTRACT(EPOCH FROM (email_confirmed_at - confirmation_email_sent_at)) / 3600) as avg_hours
FROM pm_leads
WHERE email_confirmed = true;

-- Status breakdown
SELECT status, COUNT(*) FROM pm_leads GROUP BY status;
```

#### Known Issues & Fixes Applied

**Issue 1: Python datetime scoping error**
- **Error**: `cannot access local variable 'datetime' where it is not associated with a value`
- **Cause**: Duplicate `from datetime import datetime` on line 648 of `main.py`
- **Fix**: Removed duplicate import (already imported at top of file)
- **Status**: ✅ Fixed

**Issue 2: Email confirmation link not accessible**
- **Error**: `ERR_CONNECTION_REFUSED` when clicking link
- **Cause**: `BACKEND_URL` set to `http://localhost:8000` which doesn't work from external email clients
- **Fix**: Need to update environment variables to use Codespaces forwarded URLs
- **Status**: ⚠️ Pending - User needs to update `.env` files

#### Files Modified

**Backend (5 files):**
1. `apps/welcome/backend/api/email_confirmations.py` - NEW
2. `apps/welcome/backend/main.py` - MODIFIED (lead-capture endpoint, new confirm-email endpoint)
3. `apps/welcome/backend/.env` - NEEDS UPDATE (BACKEND_URL, FRONTEND_URL)

**Frontend (4 files):**
1. `apps/welcome/frontend/src/pages/ConfirmEmail.jsx` - NEW
2. `apps/welcome/frontend/src/pages/Home.jsx` - MODIFIED (removed downloads)
3. `apps/welcome/frontend/src/App.jsx` - MODIFIED (added route)
4. `apps/welcome/frontend/.env` - NEEDS UPDATE (VITE_BACKEND_URL)

**Database:**
1. `pm_leads` table - Schema updated with new columns

#### Next Steps for Testing

1. **Update Environment Variables:**
   - Set `BACKEND_URL` and `FRONTEND_URL` in backend `.env`
   - Set `VITE_BACKEND_URL` in frontend `.env`
   - Use Codespaces forwarded URLs (from PORTS tab)
   - Ensure port visibility is "Public"

2. **Restart Services:**
   ```bash
   # Backend
   cd apps/welcome/backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

   # Frontend (in new terminal)
   npm run dev
   ```

3. **Complete Testing Checklist** (see above)

4. **Production Deployment** (after testing):
   - Deploy backend first (contains new endpoints)
   - Deploy frontend (updated UI and routing)
   - Monitor email delivery rates
   - Check analytics after first week

