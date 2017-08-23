import os

from flask import render_template, abort, flash, redirect, url_for, request, send_from_directory, current_app, make_response
from flask_login import login_required, current_user
import pdfkit

from . import main
from app import htmltopdf
from .forms import CreateEventForm, CreateTicketForm
from .. import photos, db
from ..utils import flash_errors
from ..decorators import admin_required
from ..models import User, Event, Ticket, Account, Purchase
from ..controllers import get_event_tickets_query

@main.route('/add_ticket/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_ticket(event_id):
    event = Event.query.filter_by(id=event_id).first_or_404()
    form = CreateTicketForm()
    types =filter(lambda x: x[1] not in [ticket.type for ticket in event.tickets], [(k,v ) for (k, v) in enumerate(current_app.config['TICKET_TYPES'])])
    form.type.choices = types
    if form.validate_on_submit():
        types = current_app.config['TICKET_TYPES']
        # flash(types[1])
        ticket = Ticket(type=types[form.type.data], count=form.count.data, price=form.price.data)
        ticket.event_id = event_id
        db.session.add(ticket)
        db.session.commit()
        flash("Ticket added.", category="success")
        return redirect(url_for(".get_event", id=event_id))
    else:
        flash_errors(form)
    abort(405)

@main.route('/verify_ticket/<string:ticket_hash>')
@login_required
@admin_required
def verify_ticket(hash):
    pass


@main.route('/email_ticket/<string:ticket_hash>')
def mail_ticket(ticket_hash):
    subject = "Mail with PDF"
    receiver = "receiver@mail.com"
    mail_to_be_sent = Message(subject=subject, recipients=[receiver])
    mail_to_be_sent.body = "This email contains PDF."
    pdf = create_pdf.apply_async(args=[payload], countdown=10)
    # pdf = create_pdf(render_template('your/template.html'))
    mail_to_be_sent.attach("file.pdf", "application/pdf", pdf.getvalue())
    mail_ext.send(mail_to_be_sent)
    return redirect(url_for('other_view'))

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