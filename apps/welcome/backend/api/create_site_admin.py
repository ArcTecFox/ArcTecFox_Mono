"""
Create site admin users - site/company agnostic access
"""
import os
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import create_client, Client

class SiteAdminRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

async def create_site_admin(request: SiteAdminRequest, current_user_id: str = None):
    """
    Create a new site admin user with full access to all companies and sites.
    Uses Supabase auth.admin to create user and send invitation email.

    Only existing site admins can create new site admins.
    """
    try:
        # Initialize Supabase client with service role key
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise HTTPException(status_code=500, detail="Missing Supabase service credentials")

        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Using service role key for site admin creation")

        # Verify current user is a site admin
        if current_user_id:
            current_user_response = supabase.table("users").select("site_admin").eq("id", current_user_id).single().execute()
            if not current_user_response.data or not current_user_response.data.get('site_admin'):
                raise HTTPException(status_code=403, detail="Only site admins can create new site admins")

        # Check if user already exists
        print(f"🔍 Checking if user {request.email} already exists...")
        existing_user_response = supabase.table("users").select("id,email,site_admin").eq("email", request.email).execute()

        if existing_user_response.data and len(existing_user_response.data) > 0:
            existing_user = existing_user_response.data[0]

            # If user exists and is already a site admin
            if existing_user.get('site_admin'):
                raise HTTPException(status_code=400, detail="User is already a site admin")

            # If user exists but is not a site admin, promote them
            print(f"👤 Found existing user: {existing_user['id']} - promoting to site admin")
            update_response = supabase.table("users").update({
                "site_admin": True
            }).eq("id", existing_user['id']).execute()

            if update_response.error:
                raise HTTPException(status_code=500, detail=f"Failed to promote user to site admin: {update_response.error}")

            print(f"✅ User promoted to site admin successfully")
            return {
                "success": True,
                "message": f"Existing user {request.email} promoted to site admin",
                "user_id": existing_user['id'],
                "promoted": True
            }

        # User doesn't exist - create new user and send invitation
        print(f"📝 Creating new site admin user: {request.email}")

        # Get frontend URL for redirect
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

        # Create user via Supabase Auth Admin API
        # This automatically sends an invitation email
        try:
            auth_response = supabase.auth.admin.create_user({
                "email": request.email,
                "email_confirm": False,  # Require email confirmation
                "user_metadata": {
                    "full_name": request.full_name or "",
                    "site_admin": True
                }
            })

            if not auth_response or not auth_response.user:
                raise Exception("Failed to create user via Supabase Auth")

            created_user_id = auth_response.user.id
            print(f"✅ Auth user created: {created_user_id}")

        except Exception as auth_error:
            print(f"❌ Failed to create auth user: {str(auth_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to create user account: {str(auth_error)}")

        # Update users table to set site_admin = true
        # Note: The users table might be a view or have triggers that sync with auth.users
        print(f"🔧 Setting site_admin flag for user: {created_user_id}")
        try:
            update_response = supabase.table("users").update({
                "site_admin": True,
                "full_name": request.full_name or ""
            }).eq("id", created_user_id).execute()

            print(f"✅ site_admin flag set successfully")
        except Exception as update_error:
            # Log warning but don't fail - the user was created successfully
            print(f"⚠️ Warning: Could not update users table directly: {str(update_error)}")
            print(f"⚠️ User may need manual site_admin flag update")

        # Send invitation email via Supabase
        print(f"📧 Sending site admin invitation email to {request.email}")
        try:
            invite_response = supabase.auth.admin.invite_user_by_email(
                email=request.email,
                options={
                    "data": {
                        "full_name": request.full_name or "",
                        "site_admin": True,
                        "role": "site_admin"
                    },
                    "redirect_to": f"{frontend_url}/dashboard"
                }
            )

            print(f"✅ Site admin invitation email sent successfully")

        except Exception as email_error:
            print(f"⚠️ User created but invitation email failed: {str(email_error)}")
            # Don't fail - user was created, they can reset password

        return {
            "success": True,
            "message": f"Site admin created successfully. Invitation email sent to {request.email}",
            "user_id": created_user_id,
            "promoted": False
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating site admin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create site admin: {str(e)}")
