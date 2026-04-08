import httpx
import json

API_KEY = "re_U9zfB6Q4_G9jXcA4ytFFp7Zffvg2UZ2UK"

response = httpx.post(
    "https://api.resend.com/emails",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "from": "onboarding@resend.dev",
        "to": "rishabhshuklasniper@gmail.com",
        "subject": "Test from AIML Club",
        "html": "<h1>It works!</h1>",
    },
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
