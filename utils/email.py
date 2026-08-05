import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ahmadmashhood.am@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_reset_email(to_email: str, reset_token: str, frontend_url: str = None) -> bool:
    """
    Sends a password reset link email using Gmail SMTP.
    """
    base_url = (frontend_url or DEFAULT_FRONTEND_URL).rstrip("/")
    reset_link = f"{base_url}/reset-password?token={reset_token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "FoodGenie - Reset Your Password"
    msg["From"] = f"FoodGenie Support <{SMTP_EMAIL}>"
    msg["To"] = to_email

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e9ecef; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .brand {{ font-size: 28px; font-weight: 800; color: #FF6B35; text-align: center; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 1px; }}
            .title {{ font-size: 20px; font-weight: 700; color: #2B2D42; text-align: center; margin-bottom: 16px; }}
            .text {{ font-size: 15px; color: #4A4E69; line-height: 1.6; text-align: center; margin-bottom: 24px; }}
            .btn-wrapper {{ text-align: center; margin: 28px 0; }}
            .btn {{ background-color: #FF6B35; color: #ffffff !important; padding: 14px 32px; border-radius: 12px; font-weight: 700; font-size: 16px; text-decoration: none; display: inline-block; box-shadow: 0 4px 12px rgba(255,107,53,0.3); transition: all 0.2s; }}
            .badge {{ font-size: 13px; color: #d9534f; background-color: #fdf7f7; padding: 8px 16px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: 600; }}
            .footer {{ border-top: 1px solid #edf2f7; margin-top: 32px; padding-top: 20px; text-align: center; font-size: 12px; color: #8d99ae; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="brand">🍕 FoodGenie</div>
            <div class="title">Reset Your Password 🔑</div>
            <p class="text">
                You requested to reset your FoodGenie account password. Click the button below to complete your password reset:
            </p>
            <div class="btn-wrapper">
                <a href="{reset_link}" class="btn" target="_blank">Reset Password 🔑</a>
            </div>
            <div class="badge">
                ⏰ This link expires in 30 minutes
            </div>
            <p class="text" style="font-size: 13px; color: #8d99ae;">
                If you did not request this password reset, please ignore this email and your password will remain unchanged.
            </p>
            <div class="footer">
                <p>FoodGenie — Smart Food Recommendation & Local Vendor Platform</p>
                <p>Vehari, Pakistan</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        if not SMTP_PASSWORD:
            print(f"⚠️ [SMTP NOTICE] SMTP_PASSWORD not configured in .env. Reset Link generated: {reset_link}")
            return False

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"✅ Reset password email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending reset email to {to_email}: {e}")
        print(f"🔗 Generated Reset Link: {reset_link}")
        return False


def send_welcome_email(to_email: str, user_name: str, login_url: str = None) -> bool:
    """
    Sends a welcome email to newly registered users.
    """
    target_login = login_url or f"{DEFAULT_FRONTEND_URL}/login"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to FoodGenie!"
    msg["From"] = f"FoodGenie <{SMTP_EMAIL}>"
    msg["To"] = to_email

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e9ecef; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .brand {{ font-size: 28px; font-weight: 800; color: #FF6B35; text-align: center; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 1px; }}
            .title {{ font-size: 22px; font-weight: 700; color: #2B2D42; text-align: center; margin-bottom: 16px; }}
            .text {{ font-size: 15px; color: #4A4E69; line-height: 1.6; text-align: center; margin-bottom: 24px; }}
            .btn-wrapper {{ text-align: center; margin: 28px 0; }}
            .btn {{ background-color: #FF6B35; color: #ffffff !important; padding: 14px 32px; border-radius: 12px; font-weight: 700; font-size: 16px; text-decoration: none; display: inline-block; box-shadow: 0 4px 12px rgba(255,107,53,0.3); }}
            .footer {{ border-top: 1px solid #edf2f7; margin-top: 32px; padding-top: 20px; text-align: center; font-size: 12px; color: #8d99ae; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="brand">🍕 FoodGenie</div>
            <div class="title">Welcome {user_name} to FoodGenie! 🎉</div>
            <p class="text">
                Start ordering delicious food from local vendors in Vehari with personalized recommendations and fast delivery.
            </p>
            <div class="btn-wrapper">
                <a href="{target_login}" class="btn" target="_blank">Login to Account</a>
            </div>
            <div class="footer">
                <p>FoodGenie — Smart Food Recommendation Platform</p>
                <p>Vehari, Pakistan</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        if not SMTP_PASSWORD:
            print(f"⚠️ [SMTP NOTICE] SMTP_PASSWORD not configured. Welcome email skipped for {to_email}.")
            return False

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"✅ Welcome email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending welcome email to {to_email}: {e}")
        return False
