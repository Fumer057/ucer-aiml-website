"""Email sending utilities. Falls back to console logging if SMTP is not configured."""

import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_verification_email(to_email: str, token: str):
    """Send an email verification link via Resend API."""
    verification_url = f"{settings.BASE_URL}/api/auth/verify?token={token}"

    if not settings.RESEND_API_KEY:
        # Dev mode fallback
        print(f"\n📧 [RESEND DEV] Verification email for {to_email}:")
        print(f"   👉 {verification_url}\n")
        return

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.FROM_EMAIL,
                    "to": to_email,
                    "subject": f"Verify your {settings.APP_NAME} account",
                    "html": f"""
                    <div style="font-family: sans-serif; padding: 20px;">
                        <h2>Welcome to {settings.APP_NAME}! 🎉</h2>
                        <p>Click the button below to verify your email address:</p>
                        <a href="{verification_url}" style="background: #4361EE; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Verify Email →</a>
                    </div>
                    """,
                },
            )
            response.raise_for_status()
            logger.info(f"Verification email sent via Resend to {to_email}")
    except Exception as e:
        logger.error(f"Resend API Failed: {e}")
        print(f"\n[EMAIL ERROR] Resend API Failed for {to_email}: {e}")
        print(f"Manual verification link: {verification_url}\n")
