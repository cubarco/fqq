import zbar
import qrcode

from cStringIO import StringIO
from PIL import Image


def qr_rawtostring(data):
    pil = Image.open(StringIO(data)).convert('L')
    width, height = pil.size
    raw = pil.tobytes()

    scanner = zbar.ImageScanner()
    image = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(image)

    return (i.data for i in image).next()


def qr_printraw(data):
    string = qr_rawtostring(data)
    if string:
        qr = qrcode.QRCode()
        qr.add_data(string)
        qr.print_ascii(invert=True)
