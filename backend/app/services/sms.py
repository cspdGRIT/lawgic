"""SMS delivery for mobile OTP login.

No SMS provider is truly "open source" end-to-end — actual delivery always
crosses a telecom carrier somewhere. What this module gives you is a
pluggable sender with two backends that involve no proprietary paid API:

- "console" (default): logs the code server-side instead of sending it.
  Correct for local dev / self-testing — no SMS account of any kind needed.
- "android_gateway": talks to https://github.com/android-sms-gateway/server,
  an open-source, self-hosted HTTP-to-SMS bridge you run on a spare Android
  phone with a SIM in it. Free, no vendor, no per-message billing to a
  third party — the trade-off is it's your phone's SIM sending the texts,
  so it's meant for low/medium volume, not a bulk marketing blast.

To wire in a paid aggregator (MSG91, Twilio, etc.) later, add a branch here —
the request/verify endpoints in api/v1/auth.py don't need to change.
"""

import httpx

from app.core.config import settings


async def send_otp_sms(phone: str, otp: str) -> None:
    message = (
        f"{otp} is your Lawgic verification code. "
        f"Valid for {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this with anyone."
    )

    if settings.SMS_PROVIDER == "android_gateway":
        await _send_via_android_gateway(phone, message)
    else:
        # Dev fallback: no SMS account required. print() (not logging — a bare
        # logger here has no configured handler/level and would silently drop
        # this) so the code reliably shows up wherever stdout is captured.
        print(f"[dev SMS -> {phone}] {message}", flush=True)


async def _send_via_android_gateway(phone: str, message: str) -> None:
    if not (settings.SMS_GATEWAY_URL and settings.SMS_GATEWAY_LOGIN and settings.SMS_GATEWAY_PASSWORD):
        raise RuntimeError(
            "SMS_PROVIDER=android_gateway requires SMS_GATEWAY_URL, SMS_GATEWAY_LOGIN, "
            "SMS_GATEWAY_PASSWORD to be set (see backend/.env.example)."
        )
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{settings.SMS_GATEWAY_URL.rstrip('/')}/api/3rdparty/v1/message",
            auth=(settings.SMS_GATEWAY_LOGIN, settings.SMS_GATEWAY_PASSWORD),
            json={"textMessage": {"text": message}, "phoneNumbers": [phone]},
        )
        resp.raise_for_status()
