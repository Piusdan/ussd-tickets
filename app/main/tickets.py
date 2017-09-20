from flask import render_template, make_response
import pdfkit

from app.main import main
from app.models import  Purchase


@main.route('/download/<string:code>')
def download_ticket(code):
    ticket = Purchase.query.filter_by(code=code).first()
    user = ticket.account.holder
    rendered = render_template('events/purchase.html', purchase=ticket, user=user)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['content-Disposition'] = 'inline; filename=output.pdf'

@main.route('/ticket/<string:code>')
def get_purchase(code):
    purchase = Purchase.query.filter_by(code=code).first()
    user = purchase.account.holder
    return render_template('events/purchase.html', purchase=purchase, user=user)