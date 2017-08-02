import os
from flask import render_template, abort, flash, redirect, url_for, request, send_from_directory, current_app
from ..utils import flash_errors
from flask_login import login_required, current_user
from ..decorators import admin_required
from ..models import User, Event, Ticket, Account
from .. import photos, db
from ..controllers import get_event_tickets_query
from . import main
from .forms import CreateEventForm, CreateTicketForm

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
        flash("Ticket added.", category="msg")
        return redirect(url_for(".get_event", id=event_id))
    else:
        flash_errors(form)

    return render_template('events/create_ticket.html', form=form, event=event, tickets=event.tickets)
