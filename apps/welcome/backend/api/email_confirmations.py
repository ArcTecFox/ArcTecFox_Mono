"""
Email confirmation functions for free PM plan flow
Now using Resend Templates for HTML/copy.
"""
import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def _load_logo_bytes() -> Optional[bytes]:
    """
    Load the ArcTecFox logo from the frontend assets folder and return raw bytes.
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
            return f.read()

    except Exception as e:
        logger.error(f"Error loading logo for email: {e}")
        return None


async def send_confirmation_email(email: str, full_name: str, token: str, asset_name: str):
    """
    Email #1 – Confirmation Email (Resend Template: arcfox-confirmation)

    Subject: "Confirm Your Email to Receive Your Free PM Plan"
    """
    import resend

    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating confirmation email")
        print(f"Simulated confirmation email to: {email}")
        print(f"  Confirmation token: {token}")
        print(f"  Asset: {asset_name}")
        return {"status": "simulated"}

    resend.api_key = os.getenv("RESEND_API_KEY")

    # Build confirmation URL (backend route that handles token)
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    confirmation_link = f"{backend_url}/api/confirm-email/{token}"

    # ✅ New subject line
    subject = "Confirm Your Email to Receive Your Free PM Plan"

    # Inline logo attachment (CID)
    logo_bytes = _load_logo_bytes()
    attachments = []

    if logo_bytes:
        attachments.append({
            "filename": "ArcTecFox-logo.jpg",
            "content": list(logo_bytes),   # raw bytes -> list[int], per Resend docs
            "content_id": "arcfox-logo",   # must match src="cid:arcfox-logo" in the template
            "content_type": "image/jpeg",
        })

    safe_name = full_name or "there"

    params = {
        "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
        "to": [email],
        "subject": subject,
        "template": {
            "id": "arcfox-confirmation",  # Resend template ID/alias
            "variables": {
                "name": safe_name,
                "asset_name": asset_name,
                "confirm_url": confirmation_link,
                "year": datetime.utcnow().year,
            },
        },
    }

    if attachments:
        params["attachments"] = attachments

    try:
        response = resend.Emails.send(params)
        logger.info(f"✅ Confirmation email sent to {email}: {response}")
        email_id = response.get("id") if isinstance(response, dict) else None
        return {"status": "sent", "email_id": email_id}

    except Exception as e:
        logger.error(f"❌ Error sending confirmation email: {e}")
        raise


async def send_delivery_email(email: str, full_name: str, pdf_path: str, asset_name: str):
    """
    Email #2 – PM Plan Delivery (Resend Template: arcfox-pm-plan-delivery)

    Subject: "Your Preventive Maintenance Plan for {asset_name} Is Ready"
    """
    import resend

    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating delivery email")
        print(f"Simulated delivery email to: {email}")
        print(f"  PDF path: {pdf_path}")
        return {"status": "simulated"}

    resend.api_key = os.getenv("RESEND_API_KEY")

    frontend_url = os.getenv("FRONTEND_URL", "https://arctecfox-mono.vercel.app")
    demo_url = os.getenv("DEMO_URL", f"{frontend_url}/demo")

    # ✅ New subject line, personalized with asset name
    subject = f"Your Preventive Maintenance Plan for {asset_name} Is Ready"

    # Attach logo as CID
    logo_bytes = _load_logo_bytes()
    attachments = []

    if logo_bytes:
        attachments.append({
            "filename": "ArcTecFox-logo.jpg",
            "content": list(logo_bytes),
            "content_id": "arcfox-logo",
            "content_type": "image/jpeg",
        })

    # Attach PDF plan
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except FileNotFoundError:
        logger.error(f"PDF not found at {pdf_path}")
        raise

    attachments.append({
        "filename": f"PM_Plan_{asset_name.replace(' ', '_')}.pdf",
        "content": list(pdf_bytes),
        "content_type": "application/pdf",
    })

    safe_name = full_name or "there"

    params = {
        "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
        "to": [email],
        "subject": subject,
        "template": {
            "id": "arcfox-pm-plan-delivery",
            "variables": {
                "name": safe_name,
                "asset_name": asset_name,
                "demo_url": demo_url,
                "year": datetime.utcnow().year,
            },
        },
        "attachments": attachments,
    }

    try:
        response = resend.Emails.send(params)
        logger.info(f"✅ Delivery email sent to {email}: {response}")
        email_id = response.get("id") if isinstance(response, dict) else None
        return {"status": "sent", "email_id": email_id}

    except Exception as e:
        logger.error(f"❌ Error sending delivery email: {e}")
        raise


async def send_plan_generated_notification(email: str, full_name: str, company_name: str, asset_name: str):
    """
    Internal notification to support when a free PM plan email is confirmed.
    (Still using inline HTML; can be converted to a template later if you want.)
    """
    import resend

    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating support notification")
        print(f"Simulated support notification for: {email}")
        return {"status": "simulated"}

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
        response = resend.Emails.send({
            "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
            "to": ["support@arctecfox.co"],
            "subject": subject,
            "html": html_content,
        })

        logger.info(f"✅ Plan confirmation notification sent to support: {response}")
        email_id = response.get("id") if isinstance(response, dict) else None
        return {"status": "sent", "email_id": email_id}

    except Exception as e:
        logger.error(f"❌ Error sending support notification: {e}")
        # Don't fail the request if notification fails
        return {"status": "failed", "error": str(e)}
