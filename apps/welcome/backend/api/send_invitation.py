"""
Send invitation emails to users
"""
import os
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
import resend
from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize Resend (or use another email service)
# You'll need to sign up for Resend and get an API key
# resend.api_key = os.getenv("RESEND_API_KEY")

class InvitationRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    invitation_token: str
    site_id: str

async def send_invitation_email(request: InvitationRequest):
    """Send invitation email to user"""
    try:
        # Get site and company details
        site_response = supabase.table("sites").select("*, companies(*)").eq("id", request.site_id).single().execute()
        if not site_response.data:
            raise HTTPException(status_code=404, detail="Site not found")
        
        site = site_response.data
        company_name = site['companies']['name'] if site.get('companies') else 'the company'
        site_name = site['name']
        
        # Create invitation link
        # Update this to match your frontend URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        invitation_link = f"{frontend_url}/accept-invitation?token={request.invitation_token}"
        
        # Email content
        recipient_name = request.full_name or "there"
        subject = f"You're invited to join {company_name} - {site_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4A90E2; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #4A90E2; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to ArcTecFox PM Planner</h1>
                </div>
                <div class="content">
                    <h2>Hi {recipient_name},</h2>
                    
                    <p>You've been invited to join <strong>{company_name} - {site_name}</strong> on ArcTecFox PM Planner, 
                    a preventive maintenance planning platform.</p>
                    
                    <p>Click the button below to accept this invitation:</p>
                    
                    <div style="text-align: center;">
                        <a href="{invitation_link}" class="button">Accept Invitation</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 3px;">
                        {invitation_link}
                    </p>
                    
                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>If you're new, you'll be prompted to create an account using Google Sign-In</li>
                        <li>If you already have an account, just sign in</li>
                        <li>You'll automatically gain access to {site_name}</li>
                    </ul>
                    
                    <p>This invitation will expire in 7 days.</p>
                    
                    <div class="footer">
                        <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                        <p>© 2024 ArcTecFox. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {recipient_name},
        
        You've been invited to join {company_name} - {site_name} on ArcTecFox PM Planner.
        
        Accept this invitation by visiting:
        {invitation_link}
        
        This invitation will expire in 7 days.
        
        If you didn't expect this invitation, you can safely ignore this email.
        """
        
        # For development, just log the email
        # In production, uncomment the Resend code below
        print(f"📧 Would send email to {request.email}")
        print(f"Subject: {subject}")
        print(f"Link: {invitation_link}")
        
        # Uncomment this when you have Resend API key:
        # response = resend.Emails.send({
        #     "from": "noreply@arctecfox.com",
        #     "to": request.email,
        #     "subject": subject,
        #     "html": html_content,
        #     "text": text_content
        # })
        
        return {"success": True, "message": "Invitation email sent successfully"}
        
    except Exception as e:
        print(f"Error sending invitation email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send invitation email: {str(e)}")