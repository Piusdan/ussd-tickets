from flask import render_template, make_response,jsonify, request, current_app as app
from json import dumps
import pdfkit

from app import db
from app.main import main
from app.models import  Purchase, Ticket


@main.route('/ticket/update', methods=['POST', 'GET'])
def edit_ticket():
    data = request.get_json()
    ticket_id = data.get("ticket_id")
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    print ticket
    if ticket is None:
        response = jsonify(error="Invalid Ticket")
        response.status_code = 404
    else:
        ticket.price = float(data.get("price"))
        ticket.count = int(data.get("count"))
        db.session.commit()
        response = jsonify(data="Ticket updated")
        response.status_code = 200
    return response


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

