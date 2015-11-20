import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics import barcode
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER


# TODO customize get string from db config?
def label(data):
    pdf_file_name = tempfile.mktemp(".pdf")
    styles = getSampleStyleSheet()
    h1 = styles["h1"]
    h1.alignment=TA_CENTER
    h1.fontSize = 36
    h1.spaceBefore = 10
    h1.spaceAfter = 22
    normal = styles["Normal"]
    normal.alignment=TA_CENTER
    normal.fontSize = 16
    normal.spaceAfter = 18

    normal2 = styles["BodyText"]
    normal2.alignment=TA_CENTER
    normal2.fontSize = 16
    normal2.spaceAfter = 6

    doc = SimpleDocTemplate (pdf_file_name)
    doc.pagesize = (8*cm, 29*cm)
    doc.topMargin = 0
    doc.leftMargin = 0
    doc.rightMargin = 0
    parts = list()
    parts.append(Paragraph(data['name'], normal))
    languages = list()
    for lang in data['languages']:
        if lang['correct'] and lang['lang'] not in languages:
            languages.append(lang['lang'])

    parts.append(Paragraph(' '.join(languages), normal))

    parts.append(Paragraph('%s' % data['score'], h1))

    d = barcode.createBarcodeDrawing("QR", width=4*cm, height=4*cm, barBorder=0, value="http://gestionair.ch/#/score/%s" % data['game'])
    d.hAlign = "CENTER"
    d.vAlign = "TOP"
    parts.append(d)

    parts.append(Paragraph('gestionair.ch', normal2))
    parts.append(Paragraph('code: %s' % data['game'], normal2))
    doc.build(parts)
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
    parts.append(Paragraph("TODO TEXT FROM DB?", normal))
    d = barcode.createBarcodeDrawing("QR", width=4*cm, height=4*cm, barBorder=0, value=qrcode_value)
    d.hAlign = "CENTER"
    d.vAlign = "TOP"
    parts.append(d)
    parts.append(Paragraph(str(number), h1))
    parts.append(Paragraph("TODO more text", normal))
    doc.build(parts)
    return pdf_file_name
