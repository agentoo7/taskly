"""Test script to send email via SMTP (MailHog)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

# Email content
subject = "Test Email from Taskly"
from_email = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
to_email = "test@example.com"

sendgrid_status = "Configured" if settings.SENDGRID_API_KEY else "Not set (using SMTP)"

html_content = f"""
<html>
<head></head>
<body>
    <h1>🎉 Email Test Successful!</h1>
    <p>This is a test email from Taskly.</p>
    <p>If you're seeing this in MailHog, the email system is working correctly!</p>
    <hr>
    <p style="color: gray; font-size: 12px;">
        Sent via: {settings.SMTP_HOST}:{settings.SMTP_PORT}<br>
        SMTP Host: {settings.SMTP_HOST}<br>
        SendGrid API Key: {sendgrid_status}
    </p>
</body>
</html>
"""

# Create message
msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = from_email
msg["To"] = to_email

# Attach HTML content
html_part = MIMEText(html_content, "html")
msg.attach(html_part)

# Send via SMTP
print(f"📧 Sending test email...")
print(f"   From: {from_email}")
print(f"   To: {to_email}")
print(f"   SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
print(f"   SendGrid: {'Enabled' if settings.SENDGRID_API_KEY else 'Disabled'}")
print()

try:
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
    print("✅ Email sent successfully!")
    print()
    print("🔗 View email in MailHog:")
    print("   http://localhost:8025")
    print()
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    print(f"   Error type: {type(e).__name__}")
