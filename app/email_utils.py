"""Email sending utilities. Falls back to console logging if SMTP is not configured."""

import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_verification_email(to_email: str, token: str):
    """Send an email verification link. Falls back to console in dev mode."""
    verification_url = f"{settings.BASE_URL}/api/auth/verify?token={token}"

    if not settings.SMTP_HOST:
        # Dev mode: print to console
        logger.info("=" * 60)
        logger.info("📧 VERIFICATION EMAIL (dev mode — no SMTP configured)")
        logger.info(f"   To: {to_email}")
        logger.info(f"   Link: {verification_url}")
        logger.info("=" * 60)
        print(f"\n📧 Verification email for {to_email}:")
        print(f"   👉 {verification_url}\n")
        return

    # Production: send via SMTP
    try:
        import aiosmtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = f"Verify your {settings.APP_NAME} account"
        msg.set_content(
            f"Welcome to {settings.APP_NAME}!\n\n"
            f"Click the link below to verify your email:\n"
            f"{verification_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you didn't sign up, you can safely ignore this email."
        )
        msg.add_alternative(
            f"""
            <html>
            <body style="font-family: 'DM Sans', sans-serif; background: #F8F9FF; padding: 40px;">
                <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 24px rgba(67,97,238,0.08);">
                    <h2 style="font-family: 'Outfit', sans-serif; color: #0F0F1A;">Welcome to {settings.APP_NAME}! 🎉</h2>
                    <p style="color: #6B7280; line-height: 1.7;">Click the button below to verify your email address and activate your membership.</p>
                    <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #4361EE, #7209B7); color: white; padding: 14px 34px; border-radius: 50px; text-decoration: none; font-weight: 600; margin: 20px 0;">Verify Email →</a>
                    <p style="color: #9CA3AF; font-size: 0.85rem;">This link expires in 24 hours. If you didn't sign up, ignore this email.</p>
                </div>
            </body>
            </html>
            """,
            subtype="html",
        )

        print(f"DEBUG: Attempting to send email to {to_email} via {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        print(f"DEBUG: Email successfully sent to {to_email}")
        logger.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        # Don't raise — registration should still work even if email fails
        print(f"\n[SMTP ERROR] Failed to send email to {to_email}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Detail: {str(e)}")
        print(f"Manual verification link: {verification_url}\n")
