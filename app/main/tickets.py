from flask import render_template, make_response,jsonify, Response, request, current_app as app
from json import dumps
from cStringIO import StringIO

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


@main.route('/ticket/add/{int:event_id}', methods=['POST', 'GET'])
def add_ticket(event_id):
    data = request.get_json()
    ticket = Ticket()
    ticket.event_id = event_id
    ticket.type = data.get("ticket_type")
    ticket.price = float(data.get("price"))
    ticket.count = int(data.get("count"))
    db.session.add(ticket)
    db.session.commit()
    response = jsonify(data="Ticket Created")
    response.status_code = 201
    return response


@main.route('/download/<string:code>')
def download_ticket(code):
    ticket = Purchase.query.filter_by(code=code).first()
    user = ticket.account.holder
    pdf_data = render_template('events/print_ticket.html', purchase=ticket, user=user)
    result = StringIO()
    print type(pdf_data)
    pisa.CreatePDF(
        StringIO(pdf_data.encode("utf-8")),
        dest=result)
    response = make_response(result.getvalue())
    result.close()
    ticket_name = 'ticket{code}'.format(code=code)
    # response.headers.set('Content-Disposition', 'attachment', filename=ticket_name + '.pdf')
    response.headers['Content-Type'] = 'application/pdf'
    return response

@main.route('/ticket/<string:code>')
def get_purchase(code):
    purchase = Purchase.query.filter_by(code=code).first()
    user = purchase.account.holder
    return render_template('events/purchase.html', purchase=purchase, user=user)

