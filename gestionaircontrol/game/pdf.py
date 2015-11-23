# -*- coding: UTF-8 -*-
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics import barcode
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF

from gestionaircontrol.callcenter.models import get_player_languages


# TODO: get string from db config?
def label(player):
    languages = get_player_languages(player)
    if not languages:
        languages = ['FR']

    pdf_file_name = tempfile.mktemp(".pdf")
    c = canvas.Canvas(pdf_file_name, pagesize=(76*mm, 51*mm))
    c.drawImage('/var/gestionair/control/gestionaircontrol/static/hello.jpg', 0, 0, width=76*mm, height=51*mm)

    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(38*mm, 27*mm, player.name)

    c.setFont('Helvetica-Bold', 17)
    lang = '   '.join(languages)
    c.drawCentredString(38*mm, 17*mm, lang.upper())

    qr_code = QrCodeWidget("https://gestionair.ch/#/s/%s" % player.id)
    qr_code.barHeight = 13*mm
    qr_code.barWidth = 13*mm
    qr_code.barBorder = 0
    d = Drawing(13*mm, 13*mm)
    d.add(qr_code)
    renderPDF.draw(d, c, 61*mm, 2*mm)

    c.showPage()
    c.save()
    return pdf_file_name


def ticket(name, number, qrcode_value):
    pdf_file_name = tempfile.mktemp(".pdf")
    styles = getSampleStyleSheet ()
    h1 = styles["h1"]
    h1.alignment=TA_CENTER
    h1.fontSize = 36
    h1.spaceBefore = 10
    h1.spaceAfter = 22
    normal = styles["Normal"]
    normal.alignment=TA_CENTER
    normal.fontSize = 16
    doc = SimpleDocTemplate (pdf_file_name)
    doc.pagesize = (8*cm, 29*cm)
    doc.topMargin = 0
    doc.leftMargin = 0
    doc.rightMargin = 0
    parts = []
    normal.spaceAfter = 18
    parts.append(Paragraph("Gestion'air", normal))
    parts.append(Paragraph("Votre code", normal))
    d = barcode.createBarcodeDrawing("QR", width=4*cm, height=4*cm, barBorder=0, value=qrcode_value)
    d.hAlign = "CENTER"
    d.vAlign = "TOP"
    parts.append(d)
    parts.append(Paragraph(str(number), h1))
    parts.append(Paragraph("Retrouvez la HEG Arc sur", normal))
    parts.append(Paragraph("son stand au 1er étage de", normal))
    parts.append(Paragraph("Campus Arc 2", normal))
    doc.build(parts)
    return pdf_file_name
