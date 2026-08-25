"""UPI QR generation — no payment gateway, no webhook. Just the standard UPI deep-link
URI (upi://pay?...) rendered as a QR code so a phone's UPI app can scan-to-pay. Fully
open source: the `qrcode` package generates the image locally, no external API call."""

import base64
import io
from urllib.parse import quote

import qrcode

from app.core.config import settings


def build_upi_uri(transaction_note: str) -> str:
    params = (
        f"pa={quote(settings.UPI_VPA)}"
        f"&pn={quote(settings.UPI_PAYEE_NAME)}"
        f"&am={settings.ACCESS_FEE_RUPEES}"
        f"&cu=INR"
        f"&tn={quote(transaction_note)}"
    )
    return f"upi://pay?{params}"


def build_qr_data_uri(data: str) -> str:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
