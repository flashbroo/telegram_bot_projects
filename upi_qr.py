# upi_qr.py
# Generates a UPI QR PNG in-memory with locked amount.
# Requires: qrcode, pillow (PIL)

import qrcode
import io
from typing import Union

def generate_upi_qr(upi_id: str, name: str, amount: Union[int, float]) -> io.BytesIO:
    """
    Generate a UPI QR PNG that locks the amount.
    upi_id: e.g. 'flashbro@ybl'
    name: payee name (e.g. 'Flash Bro')
    amount: numeric amount (e.g. 60 or 999.50)
    Returns: BytesIO with PNG image (seeked to start)
    """
    # Ensure dot decimal uses dot
    amt_str = f"{float(amount):.2f}".rstrip('0').rstrip('.') if float(amount) % 1 != 0 else str(int(amount))

    # UPI deep link with locked amount (cu=INR locks currency)
    upi_uri = f"upi://pay?pa={upi_id}&pn={name}&am={amt_str}&cu=INR"

    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = io.BytesIO()
    bio.name = "upi_qr.png"
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio