from xhtml2pdf import pisa
from cStringIO import StringIO
from . import celery

# @celery.task(bind=True, default_retry_delay=30*60)
def create_pdf(pdf_data):
    """
    Convert template to pdf
    """
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf