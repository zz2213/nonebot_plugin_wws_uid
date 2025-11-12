import qrcode
from pathlib import Path
from io import BytesIO

async def generate_qrcode(url: str, path: Path) -> bool:
    """生成二维码"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(path)
        return True
    except Exception:
        return False

async def generate_qrcode_base64(url: str) -> str:
    """生成二维码base64"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        import base64
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return ""