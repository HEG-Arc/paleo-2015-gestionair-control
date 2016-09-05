# -*- coding: UTF-8 -*-
import tempfile
from gestionaircontrol.game.models import get_config_value

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Flowable
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

from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from config.settings import APPS_DIR
from gestionaircontrol.callcenter.models import get_player_languages
import os


def form_xo_reader(imgdata):
    page, = PdfReader(imgdata).pages
    return pagexobj(page)


class PdfImage(Flowable):
    def __init__(self, img_data, width=76*mm, height=51*mm):
        self.img_width = width
        self.img_height = height
        self.img_data = img_data

    def wrap(self, width, height):
        return self.img_width, self.img_height

    def drawOn(self, canv, x, y, _sW=0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        img = self.img_data
        if isinstance(img, PdfDict):
            xscale = self.img_width / img.BBox[2]
            yscale = self.img_height / img.BBox[3]
            canv.translate(x, y)
            canv.scale(xscale, yscale)
            canv.doForm(makerl(canv, img))
        else:
            canv.drawImage(img, x, y, self.img_width, self.img_height)
        canv.restoreState()


# TODO: get string from db config?
def label(player):
    languages = get_player_languages(player)
    if not languages:
        languages = ['FR']

    imgdata = open(APPS_DIR.path('static/capacite.pdf').__str__(), 'r')
    imgdata.seek(0)
    reader = form_xo_reader
    image = reader(imgdata)
    pdf_file_name = tempfile.mktemp(".pdf")
    c = canvas.Canvas(pdf_file_name, pagesize=(76*mm, 51*mm))
    img = PdfImage(image, width=76*mm, height=51*mm)
    img.drawOn(c, 0*mm, 0*mm)
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(38*mm, 27*mm, player.name)

    c.setFont('Helvetica-Bold', 17)
    lang = '   '.join(languages)
    c.drawCentredString(38*mm, 17*mm, lang.upper())

    qr_code = QrCodeWidget(player.url)
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
    d = barcode.createBarcodeDrawing("QR", width=4*cm, height=4*cm, barBorder=0, value=qrcode_value)
    d.hAlign = "CENTER"
    d.vAlign = "TOP"
    parts.append(d)
    parts.append(Paragraph(str(number), h1))
    parts.append(Paragraph("Mon avenir? Je le gère", normal))
    parts.append(Paragraph("www.heg-arc.ch", normal))
    doc.build(parts)
    return pdf_file_name
