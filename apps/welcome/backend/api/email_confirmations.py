"""
Email confirmation functions for free PM plan flow
"""
import os
import logging
import base64
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def _load_logo_base64() -> Optional[str]:
    """
    Load the ArcTecFox logo from the frontend assets folder and return base64-encoded content.
    Returns None if the file cannot be found/read.
    """
    try:
        # email_confirmations.py is at:
        # apps/welcome/backend/api/email_confirmations.py
        # logo is at:
        # apps/welcome/frontend/public/assets/ArcTecFox-logo.jpg
        current_dir = os.path.dirname(__file__)
        logo_path = os.path.abspath(
            os.path.join(
                current_dir,
                "..",        # -> backend
                "..",        # -> welcome
                "frontend",
                "public",
                "assets",
                "ArcTecFox-logo.jpg",
            )
        )

        if not os.path.exists(logo_path):
            logger.warning(f"Logo file not found at {logo_path}; emails will be sent without inline logo.")
            return None

        with open(logo_path, "rb") as f:
            logo_bytes = f.read()

        return base64.b64encode(logo_bytes).decode("utf-8")

    except Exception as e:
        logger.error(f"Error loading logo for email: {e}")
        return None


async def send_confirmation_email(email: str, full_name: str, token: str, asset_name: str):
    """
    Email #1 – Confirmation Email (Resend)

    Hi [Name],
    Your preventive maintenance plan is almost ready.
    Confirm your email so we can deliver your free plan and welcome guide.
    """
    import resend

    # Check if RESEND_API_KEY is configured
    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating confirmation email")
        print(f"Simulated confirmation email to: {email}")
        print(f"  Confirmation token: {token}")
        print(f"  Asset: {asset_name}")
        return {"status": "simulated"}

    # Initialize Resend
    resend.api_key = os.getenv("RESEND_API_KEY")

    # Get backend URL for confirmation link
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    confirmation_link = f"{backend_url}/api/confirm-email/{token}"

    subject = f"Confirm your email – your PM plan for {asset_name} is almost ready"

    # Load logo as base64 (for inline CID image)
    logo_b64 = _load_logo_base64()

    # Shorter, funnel-focused copy
    safe_name = full_name or "there"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #111827; margin: 0; padding: 0; background-color: #f3f4f6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 24px; }}
            .card {{ background-color: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 24px 24px 32px; }}
            .button {{
                display: inline-block;
                padding: 14px 28px;
                background-color: #3b82f6;
                color: white !important;
                text-decoration: none;
                border-radius: 999px;
                font-weight: 600;
                font-size: 15px;
                margin: 20px 0;
            }}
            .button:hover {{ background-color: #2563eb; }}
            .footer {{
                margin-top: 24px;
                padding-top: 16px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #6b7280;
                text-align: center;
            }}
            .small-text {{ font-size: 13px; color: #4b5563; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">

                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="cid:arcfox-logo" alt="ArcTecFox Logo" style="width: 120px; height: auto;" />
                </div>

                <p class="small-text">Hi {safe_name},</p>

                <p class="small-text">
                    Your preventive maintenance plan for <strong>{asset_name}</strong> is almost ready.
                    Confirm your email so we can deliver your free plan and welcome guide.
                </p>

                <div style="text-align: center;">
                    <a href="{confirmation_link}" class="button">
                        Confirm My Email
                    </a>
                </div>

                <p class="small-text" style="margin-top: 16px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{confirmation_link}" style="color: #3b82f6; word-break: break-all;">{confirmation_link}</a>
                </p>

                <div class="footer">
                    <p>&copy; {datetime.utcnow().year} ArcTecFox. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Build attachments list (logo as inline image if available)
        attachments = []
        if logo_b64:
            attachments.append({
                "filename": "ArcTecFox-logo.jpg",
                "content": logo_b64,          # base64-encoded content
                "content_id": "arcfox-logo",  # must match src="cid:arcfox-logo"
                "content_type": "image/jpeg",
            })

        # Send email using Resend
        params = {
            "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
            "to": [email],
            "subject": subject,
            "html": html_content,
        }
        if attachments:
            params["attachments"] = attachments

        response = resend.Emails.send(params)

        logger.info(f"✅ Confirmation email sent to {email}: {response}")
        return {"status": "sent", "email_id": response.get("id")}

    except Exception as e:
        logger.error(f"❌ Error sending confirmation email: {e}")
        raise


async def send_delivery_email(email: str, full_name: str, pdf_path: str, asset_name: str):
    """
    Email #2 – PM Plan Delivery

    Hi [Name or Company],

    Welcome to ArcTecFox!
    Your preventive maintenance plan for [Asset Name] is attached below.

    This plan is tailored to help you improve reliability, reduce downtime, and optimize maintenance scheduling.
    """
    import resend

    # Check if RESEND_API_KEY is configured
    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating delivery email")
        print(f"Simulated delivery email to: {email}")
        print(f"  PDF path: {pdf_path}")
        return {"status": "simulated"}

    # Initialize Resend
    resend.api_key = os.getenv("RESEND_API_KEY")

    # Get frontend URL & optional demo URL
    frontend_url = os.getenv("FRONTEND_URL", "https://arctecfox-mono.vercel.app")
    demo_url = os.getenv("DEMO_URL", f"{frontend_url}/demo")

    subject = f"Your preventive maintenance plan for {asset_name} is ready"

    # Load logo as base64 (for inline CID image)
    logo_b64 = _load_logo_base64()
    safe_name = full_name or "there"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #111827; margin: 0; padding: 0; background-color: #f3f4f6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 24px; }}
            .card {{ background-color: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 24px 24px 32px; }}
            .cta-button {{
                display: inline-block;
                padding: 14px 28px;
                background-color: #3b82f6;
                color: white !important;
                text-decoration: none;
                border-radius: 999px;
                font-weight: 600;
                margin: 16px 0;
            }}
            .cta-button:hover {{ background-color: #2563eb; }}
            .footer {{
                margin-top: 24px;
                padding-top: 16px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #6b7280;
                text-align: center;
            }}
            .small-text {{ font-size: 13px; color: #4b5563; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">

                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 16px;">
                    <img src="cid:arcfox-logo" alt="ArcTecFox Logo" style="width: 120px; height: auto;" />
                </div>

                <p class="small-text">Hi {safe_name},</p>

                <p class="small-text">
                    <strong>Welcome to ArcTecFox!</strong><br/>
                    Your preventive maintenance plan for <strong>{asset_name}</strong> is attached below.
                </p>

                <p class="small-text">
                    This plan is tailored to help you improve reliability, reduce downtime,
                    and optimize your maintenance scheduling.
                </p>

                <p class="small-text"><strong>Next steps:</strong></p>
                <ul class="small-text">
                    <li>Download and review your PM plan.</li>
                    <li>Note any areas where you’d like revisions.</li>
                    <li>Share it with your maintenance team.</li>
                </ul>

                <p class="small-text">
                    Want to see how this integrates with your CMMS and existing workflows?
                    You can schedule a 15-minute demo here:
                </p>

                <div style="text-align: center;">
                    <a href="{demo_url}" class="cta-button">
                        Book a 15-Minute Demo
                    </a>
                </div>

                <p class="small-text">
                    Your PM Plan is attached to this email as a PDF file.
                </p>

                <div class="footer">
                    <p>Thanks for using ArcTecFox — your partner in AI-powered maintenance.</p>
                    <p>&copy; {datetime.utcnow().year} ArcTecFox. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Read PDF file and encode as base64
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        # Build attachments: logo (inline) + PDF
        attachments = []

        if logo_b64:
            attachments.append({
                "filename": "ArcTecFox-logo.jpg",
                "content": logo_b64,
                "content_id": "arcfox-logo",
                "content_type": "image/jpeg",
            })

        attachments.append({
            "filename": f"PM_Plan_{asset_name.replace(' ', '_')}.pdf",
            "content": pdf_base64,
            "content_type": "application/pdf",
        })

        # Send email with PDF + logo attachment
        response = resend.Emails.send({
            "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            "attachments": attachments,
        })

        logger.info(f"✅ Delivery email sent to {email}: {response}")
        return {"status": "sent", "email_id": response.get("id")}

    except Exception as e:
        logger.error(f"❌ Error sending delivery email: {e}")
        raise


async def send_plan_generated_notification(email: str, full_name: str, company_name: str, asset_name: str):
    """Send notification to support when a free PM plan email is confirmed"""
    import resend

    # Check if RESEND_API_KEY is configured
    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating support notification")
        print(f"Simulated support notification for: {email}")
        return {"status": "simulated"}

    # Initialize Resend
    resend.api_key = os.getenv("RESEND_API_KEY")

    subject = f"New PM Plan Confirmed - {full_name} from {company_name}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
            .info-box {{ margin: 15px 0; padding: 15px; background: white; border-left: 4px solid #22c55e; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ PM Plan Email Confirmed</h1>
            </div>
            <div class="content">
                <p>A user has confirmed their email and received their free PM plan:</p>

                <div class="info-box">
                    <strong>User Details:</strong><br>
                    <strong>Name:</strong> {full_name}<br>
                    <strong>Email:</strong> {email}<br>
                    <strong>Company:</strong> {company_name}<br>
                    <strong>Asset:</strong> {asset_name}<br>
                    <strong>Confirmed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
                </div>

                <p>This user has confirmed their email and received their PM plan PDF.</p>

                <div class="footer">
                    <p>This is an automated notification from ArcTecFox PM Planner.</p>
                    <p>Please do not reply to this email.</p>
                    <p>&copy; {datetime.utcnow().year} ArcTecFox. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Send email using Resend
        response = resend.Emails.send({
            "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
            "to": ["support@arctecfox.co"],
            "subject": subject,
            "html": html_content
        })

        logger.info(f"✅ Plan confirmation notification sent to support: {response}")
        return {"status": "sent", "email_id": response.get("id")}

    except Exception as e:
        logger.error(f"❌ Error sending support notification: {e}")
        # Don't fail the request if notification fails
        return {"status": "failed", "error": str(e)}
