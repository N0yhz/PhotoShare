import qrcode
from io import BytesIO

def generate_qr_code(data: str) -> BytesIO:
    """
    Generates a QR code from the given data and returns it as a byte stream.

    Args:
        data (str): The data to encode into the QR code.

    Returns:
        BytesIO: A byte stream containing the QR code image in PNG format.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes
