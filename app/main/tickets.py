from flask import render_template, make_response,jsonify, request, abort
from flask_login import login_required
from app.decorators import admin_required
from cStringIO import StringIO
from xhtml2pdf import pisa
import logging

from app import db
from app.main import main
from app.model import  Package, Type, Event, Ticket


@main.route('/package/update', methods=['POST', 'GET'])
def edit_package():
    data = request.get_json()
    package_id = data.get("package_id")
    package = Package.by_id(package_id)
    logging.info(data)
    if package is None:
        response = jsonify(error="Invalid Package")
        response.status_code = 404
    else:
        package.price = float(data.get("price"))
        package.remaining = int(data.get("number"))
        package.save()
        response = jsonify(data="Ticket updated")
        response.status_code = 200
    return response


@main.route('/package/add/<int:event_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def add_package(event_id):
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    logging.info("event {}".format(event_id))
    event = Event.query.get(event_id)
    if event is None:
        abort(404)
    type_id = request_dict["type"]
    price = request_dict["price"]
    number = request_dict["number"]
    package = Package.create(type_id=type_id, price=price, remaining=number, event_id=event.id)
    response = jsonify(data="Package Added")
    response.status_code = 201
    return response

@main.route('/download/<string:code>')
def download_ticket(code):
    ticket = Ticket.by_code(code)
    if ticket is None:
        abort(404)
    user = ticket.user
    pdf_data = render_template('events/print_ticket.html', ticket=ticket, user=user)
    result = StringIO()
    print type(pdf_data)
    pisa.CreatePDF(
        StringIO(pdf_data.encode("utf-8")),
        dest=result)
    response = make_response(result.getvalue())
    result.close()
    ticket_name = 'ticket{code}'.format(code=code)
    response.headers.set('Content-Disposition', 'attachment', filename='{ticket_code}_{event_name}.pdf'.format(ticket_code=ticket.code, event_name=ticket.package.event.name))
    response.headers['Content-Type'] = 'application/pdf'
    return response

@main.route('/ticket/<string:code>')
def get_purchase(code):
    ticket = Ticket.query.filter_by(code=code).first()
    user = ticket.user
    return render_template('events/purchase.html', ticket=ticket, user=user)

