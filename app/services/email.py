"""
Email Service using SendGrid

Handles automated email delivery for API key welcome emails,
contact form confirmations, and admin notifications.
"""

import os
import logging
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@golfphysics.io')
REPLY_TO_EMAIL = os.getenv('REPLY_TO_EMAIL', 'golfphysicsio@gmail.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'golfphysicsio@gmail.com')


async def send_api_key_email(
    email: str,
    name: str,
    api_key: str
) -> bool:
    """Send welcome email with API key."""

    if not SENDGRID_API_KEY:
        logger.warning(f"[EMAIL] SendGrid not configured, would send API key to {email}")
        logger.info(f"[EMAIL] API Key for {email}: {api_key}")
        return False

    subject = "Your Golf Physics API Key is Ready"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

        <div style="background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">Golf Physics API</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Professional Weather Intelligence for Golf Technology</p>
        </div>

        <div style="background: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
            <p style="font-size: 18px; margin-top: 0;">Hi {name},</p>

            <p>Welcome to Golf Physics API! Your free Developer tier API key is ready to use.</p>

            <div style="background: #f5f5f5; border-left: 4px solid #2E7D32; padding: 20px; margin: 25px 0; border-radius: 4px;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #2E7D32;">Your API Key:</p>
                <code style="background: white; padding: 12px; display: block; font-size: 14px; border: 1px solid #ddd; border-radius: 4px; word-break: break-all; font-family: 'Courier New', monospace;">
                    {api_key}
                </code>
                <p style="color: #d32f2f; font-size: 13px; margin: 10px 0 0 0;">
                    <strong>Keep this key secure</strong> - treat it like a password. It won't be shown again.
                </p>
            </div>

            <h2 style="color: #2E7D32; font-size: 20px; margin-top: 30px;">Developer Tier Includes:</h2>
            <ul style="line-height: 1.8;">
                <li>60 requests per minute</li>
                <li>1,000 requests per day (~30K/month)</li>
                <li>Real-time weather data with physics calculations</li>
                <li>Multi-unit support (imperial + metric)</li>
                <li>Complete API documentation</li>
                <li>Community support</li>
            </ul>

            <div style="background: #e8f5e9; border: 1px solid #a5d6a7; padding: 20px; margin: 25px 0; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #2E7D32;">Quick Start</h3>

                <p style="margin: 15px 0 10px 0;"><strong>1. Make your first request:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 13px; border: 1px solid #ddd;">curl "https://api.golfphysics.io/weather?lat=33.7&lon=-84.4" \\
  -H "X-API-Key: {api_key}"</pre>

                <p style="margin: 15px 0 5px 0;"><strong>2. View Documentation:</strong></p>
                <p style="margin: 5px 0;">
                    <a href="https://golfphysics.io/docs" style="color: #2E7D32; text-decoration: none; font-weight: 500;">
                        https://golfphysics.io/docs
                    </a>
                </p>

                <p style="margin: 15px 0 5px 0;"><strong>3. Explore Code Examples:</strong></p>
                <p style="margin: 5px 0;">Python, JavaScript, and Go examples available in our documentation.</p>
            </div>

            <h2 style="color: #2E7D32; font-size: 20px; margin-top: 30px;">Ready for Production?</h2>
            <p>The Developer tier is perfect for testing and development. When you're ready to scale:</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 15px; border: 1px solid #e0e0e0; background: #fafafa;">
                        <strong style="color: #2E7D32;">Professional</strong><br>
                        <span style="font-size: 24px; font-weight: bold;">$299</span><span style="color: #666;">/month</span>
                        <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; line-height: 1.6;">
                            <li>25K requests/day</li>
                            <li>99.9% uptime SLA</li>
                            <li>Phone support</li>
                        </ul>
                    </td>
                    <td style="padding: 15px; border: 1px solid #e0e0e0; background: #fafafa;">
                        <strong style="color: #2E7D32;">Business</strong><br>
                        <span style="font-size: 24px; font-weight: bold;">$599</span><span style="color: #666;">/month</span>
                        <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; line-height: 1.6;">
                            <li>100K requests/day</li>
                            <li>Account manager</li>
                            <li>Custom integration</li>
                        </ul>
                    </td>
                </tr>
            </table>

            <p style="text-align: center; margin: 25px 0;">
                <a href="https://golfphysics.io/pricing" style="display: inline-block; background: #2E7D32; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 500;">
                    View All Pricing Plans
                </a>
            </p>

            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">

            <h3 style="color: #2E7D32;">Need Help?</h3>
            <p>We're here to support you:</p>
            <ul style="line-height: 1.8;">
                <li>Email: <a href="mailto:support@golfphysics.io" style="color: #2E7D32;">support@golfphysics.io</a></li>
                <li>Documentation: <a href="https://golfphysics.io/docs" style="color: #2E7D32;">golfphysics.io/docs</a></li>
            </ul>

            <p style="margin-top: 30px;">Happy building!</p>

            <p style="margin: 5px 0;">
                <strong>The Golf Physics Team</strong><br>
                <span style="color: #666; font-size: 14px;">Professional Weather Intelligence for Golf Technology</span>
            </p>

            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">

            <p style="font-size: 13px; color: #666; font-style: italic;">
                P.S. We'd love to hear about your project! Reply to this email and tell us what you're building with Golf Physics API.
            </p>
        </div>

        <div style="text-align: center; padding: 20px; font-size: 12px; color: #666;">
            <p>&copy; 2026 Golf Physics API. All rights reserved.</p>
            <p>
                <a href="https://golfphysics.io" style="color: #2E7D32; text-decoration: none;">Website</a> |
                <a href="https://golfphysics.io/docs" style="color: #2E7D32; text-decoration: none;">Documentation</a> |
                <a href="https://golfphysics.io/pricing" style="color: #2E7D32; text-decoration: none;">Pricing</a>
            </p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Golf Physics API - Your API Key is Ready

Hi {name},

Welcome to Golf Physics API! Your free Developer tier API key is ready to use.

YOUR API KEY:
{api_key}

Keep this key secure - treat it like a password. It won't be shown again.

DEVELOPER TIER INCLUDES:
- 60 requests per minute
- 1,000 requests per day (~30K/month)
- Real-time weather data with physics calculations
- Multi-unit support (imperial + metric)
- Complete API documentation
- Community support

QUICK START:

1. Make your first request:
curl "https://api.golfphysics.io/weather?lat=33.7&lon=-84.4" \\
  -H "X-API-Key: {api_key}"

2. View Documentation: https://golfphysics.io/docs

3. Explore code examples in Python, JavaScript, and Go

READY FOR PRODUCTION?

Professional Tier - $299/month
- 25K requests/day
- 99.9% uptime SLA
- Phone support

Business Tier - $599/month
- 100K requests/day
- Account manager
- Custom integration

View all pricing: https://golfphysics.io/pricing

NEED HELP?
- Email: support@golfphysics.io
- Docs: https://golfphysics.io/docs

Happy building!

The Golf Physics Team
Professional Weather Intelligence for Golf Technology

---

P.S. We'd love to hear about your project! Reply to this email and tell us what you're building.
    """

    try:
        message = Mail(
            from_email=Email(FROM_EMAIL, "Golf Physics API"),
            to_emails=To(email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )

        # Set reply-to
        message.reply_to = Email(REPLY_TO_EMAIL)

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"[EMAIL] API key sent to {email}, status: {response.status_code}")
        return response.status_code == 202

    except Exception as e:
        logger.error(f"[EMAIL] Failed to send to {email}: {str(e)}")
        return False


async def send_contact_confirmation(
    email: str,
    name: str,
    subject: str
) -> bool:
    """Send confirmation email for contact form submission."""

    if not SENDGRID_API_KEY:
        logger.warning(f"[EMAIL] Would send contact confirmation to {email}")
        return False

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2E7D32; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
            <h1 style="margin: 0;">Golf Physics API</h1>
        </div>

        <div style="background: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
            <p>Hi {name},</p>

            <p>Thanks for reaching out! We've received your message regarding:</p>

            <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #2E7D32; margin: 20px 0;">
                <strong>{subject}</strong>
            </div>

            <p>We'll get back to you within 24 hours (usually much faster!).</p>

            <p>In the meantime, feel free to explore:</p>
            <ul>
                <li><a href="https://golfphysics.io/docs" style="color: #2E7D32;">API Documentation</a></li>
                <li><a href="https://golfphysics.io/pricing" style="color: #2E7D32;">Pricing Plans</a></li>
            </ul>

            <p style="margin-top: 30px;">Best regards,<br><strong>The Golf Physics Team</strong></p>
        </div>
    </body>
    </html>
    """

    try:
        message = Mail(
            from_email=Email(FROM_EMAIL, "Golf Physics API"),
            to_emails=To(email),
            subject="Thanks for contacting Golf Physics API",
            html_content=Content("text/html", html_content)
        )

        message.reply_to = Email(REPLY_TO_EMAIL)

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"[EMAIL] Contact confirmation sent to {email}")
        return response.status_code == 202

    except Exception as e:
        logger.error(f"[EMAIL] Failed to send contact confirmation: {str(e)}")
        return False


async def send_admin_notification(
    lead_type: str,
    lead_data: dict,
    is_high_value: bool = False
) -> bool:
    """Send admin notification about new lead."""

    if not SENDGRID_API_KEY:
        logger.info(f"[NOTIFICATION] {lead_type} lead: {lead_data}")
        return False

    priority = "HIGH VALUE" if is_high_value else "New"
    subject = f"{priority} Lead: {lead_type} - {lead_data.get('name', 'Unknown')}"

    if lead_type == "API Key Request":
        details = f"""
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Email:</td><td style="padding: 8px;">{lead_data.get('email')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Company:</td><td style="padding: 8px;">{lead_data.get('company', 'Not provided')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Use Case:</td><td style="padding: 8px;">{lead_data.get('use_case')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Expected Volume:</td><td style="padding: 8px;">{lead_data.get('expected_volume')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Description:</td><td style="padding: 8px;">{lead_data.get('description', 'Not provided')}</td></tr>
        """
    else:  # Contact Form
        details = f"""
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Email:</td><td style="padding: 8px;">{lead_data.get('email')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Company:</td><td style="padding: 8px;">{lead_data.get('company', 'Not provided')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Subject:</td><td style="padding: 8px;">{lead_data.get('subject')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Message:</td><td style="padding: 8px;">{lead_data.get('message')}</td></tr>
        """

    header_color = '#dc3545' if is_high_value else '#2E7D32'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background: {header_color}; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">{priority} Lead: {lead_type}</h1>
        </div>

        <div style="padding: 20px;">
            <h2>Lead Details:</h2>

            <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
                <tr><td style="padding: 8px; font-weight: bold; background: #f5f5f5;">Name:</td><td style="padding: 8px;">{lead_data.get('name')}</td></tr>
                {details}
            </table>

            <p style="margin-top: 30px;">
                <a href="https://api.golfphysics.io/admin/leads" style="background: #2E7D32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    View in Admin Dashboard
                </a>
            </p>
        </div>
    </body>
    </html>
    """

    try:
        message = Mail(
            from_email=Email(FROM_EMAIL, "Golf Physics API"),
            to_emails=To(ADMIN_EMAIL),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"[NOTIFICATION] Admin notified about {lead_type} lead")
        return response.status_code == 202

    except Exception as e:
        logger.error(f"[NOTIFICATION] Failed to notify admin: {str(e)}")
        return False
