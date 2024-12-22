import qrcode
from io import BytesIO


def generate_qr_code(url):
    """
    Generates a QR code for the given URL.
    :param url: URL for the QR code.
    :return: byte stream of the QR code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_image = BytesIO()
    qr.make_image(fill="black", back_color="white").save(qr_image, format="PNG")
    qr_image.seek(0)
    return qr_image
