"""
Email confirmation functions for free PM plan flow
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_confirmation_email(email: str, full_name: str, token: str, asset_name: str):
    """Send initial email confirmation request with link"""
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

    subject = f"Confirm Your Email - Free PM Plan for {asset_name}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .button {{
                display: inline-block;
                padding: 16px 32px;
                background-color: #3b82f6;
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
                margin: 20px 0;
            }}
            .button:hover {{ background-color: #2563eb; }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
            .info-box {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #3b82f6;
            }}
            .expiry-warning {{
                background: #fef3c7;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                border-left: 4px solid #f59e0b;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Confirm Your Email Address</h1>
            </div>
            <div class="content">
                <p>Hi {full_name},</p>

                <p>Thank you for generating a free Preventive Maintenance plan for <strong>{asset_name}</strong> with ArcTecFox PM Planner!</p>

                <div class="info-box">
                    <p><strong>One more step to get your PM plan:</strong></p>
                    <p>Please confirm your email address by clicking the button below. Once confirmed, we'll immediately send you a detailed PDF with your custom PM plan.</p>
                </div>

                <div style="text-align: center;">
                    <a href="{confirmation_link}" class="button">Confirm Email & Get Your PM Plan</a>
                </div>

                <p style="margin-top: 20px; font-size: 14px; color: #666;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{confirmation_link}" style="color: #3b82f6; word-break: break-all;">{confirmation_link}</a>
                </p>

                <div class="expiry-warning">
                    <strong>⏰ Important:</strong> This confirmation link expires in 24 hours for security purposes.
                </div>

                <div class="footer">
                    <p><strong>Why confirm your email?</strong></p>
                    <p>We require email confirmation to prevent spam and ensure you receive your PM plan safely.</p>
                    <p style="margin-top: 20px;">This is an automated email from ArcTecFox PM Planner.</p>
                    <p>&copy; 2024 ArcTecFox. All rights reserved.</p>
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
            "to": [email],
            "subject": subject,
            "html": html_content
        })

        logger.info(f"✅ Confirmation email sent to {email}: {response}")
        return {"status": "sent", "email_id": response.get("id")}

    except Exception as e:
        logger.error(f"❌ Error sending confirmation email: {e}")
        raise


async def send_delivery_email(email: str, full_name: str, pdf_path: str, asset_name: str):
    """Send PM plan PDF after email confirmation"""
    import resend
    import base64

    # Check if RESEND_API_KEY is configured
    if not os.getenv("RESEND_API_KEY"):
        logger.warning("RESEND_API_KEY not configured, simulating delivery email")
        print(f"Simulated delivery email to: {email}")
        print(f"  PDF path: {pdf_path}")
        return {"status": "simulated"}

    # Initialize Resend
    resend.api_key = os.getenv("RESEND_API_KEY")

    # Get frontend URL
    frontend_url = os.getenv("FRONTEND_URL", "https://arctecfox-mono.vercel.app")

    subject = f"Your PM Plan for {asset_name} - ArcTecFox"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .success-icon {{ font-size: 48px; text-align: center; margin: 20px 0; }}
            .cta-button {{
                display: inline-block;
                padding: 16px 32px;
                background-color: #3b82f6;
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .info-box {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #22c55e;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Your PM Plan is Ready!</h1>
            </div>
            <div class="content">
                <div class="success-icon">✅</div>

                <p>Hi {full_name},</p>

                <p>Great news! Your email has been confirmed and your custom Preventive Maintenance plan for <strong>{asset_name}</strong> is attached to this email.</p>

                <div class="info-box">
                    <h3>What's Included:</h3>
                    <ul>
                        <li>12 comprehensive maintenance tasks</li>
                        <li>Detailed step-by-step instructions</li>
                        <li>Recommended intervals and schedules</li>
                        <li>Safety precautions and best practices</li>
                        <li>Tools and consumables needed</li>
                        <li>Engineering rationale for each task</li>
                    </ul>
                </div>

                <h3>Next Steps:</h3>
                <ol>
                    <li>Download and review the attached PDF</li>
                    <li>Share with your maintenance team</li>
                    <li>Implement the recommended schedule</li>
                </ol>

                <div style="background: #ecfdf5; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #22c55e;">
                    <p><strong>Want to do more with ArcTecFox?</strong></p>
                    <p>Upgrade to our full platform to:</p>
                    <ul>
                        <li>Track task completion and schedules</li>
                        <li>Manage multiple assets and sites</li>
                        <li>Assign tasks to technicians</li>
                        <li>Get automated reminders and notifications</li>
                        <li>Generate compliance reports</li>
                    </ul>
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="{frontend_url}/pricing" class="cta-button">Explore Plans</a>
                    </div>
                </div>

                <div class="footer">
                    <p>Questions? Contact us at support@arctecfox.co</p>
                    <p style="margin-top: 20px;">&copy; 2024 ArcTecFox. All rights reserved.</p>
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

        pdf_base64 = base64.b64encode(pdf_content).decode()

        # Send email with PDF attachment
        response = resend.Emails.send({
            "from": "ArcTecFox PM Planner <notifications@arctecfox.ai>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            "attachments": [{
                "filename": f"PM_Plan_{asset_name.replace(' ', '_')}.pdf",
                "content": pdf_base64
            }]
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
                    <p>&copy; 2024 ArcTecFox. All rights reserved.</p>
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
