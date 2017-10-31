from flask import render_template, make_response,jsonify, request, abort
from flask_login import login_required
from app.decorators import admin_required
from cStringIO import StringIO
import logging

from app import db
from app.main import main
from app.models import  Purchase, Ticket, TicketType, Event


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


@main.route('/ticket/add/<int:event_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def add_ticket(event_id):
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    logging.info("event {}".format(event_id))
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    # if request_dict["type"] in [ticket.type_id for ticket in event.tickets]:
    #     response = jsonify(data="Cannot create ticket, ticket already exists")
    #     response.status_code = 300
    #     return response
    ticket = Ticket()
    ticket.event_id = event_id
    ticket.type_id = request_dict["type"]
    ticket.price = request_dict["price"]
    ticket.count = request_dict["count"]
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

