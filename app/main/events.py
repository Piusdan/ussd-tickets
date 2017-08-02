import os
from flask import render_template, abort, flash, redirect, url_for, request, send_from_directory, current_app

from flask_login import login_required, current_user
from ..decorators import admin_required
from ..models import User, Event, Ticket, Account
from .. import photos, db
from ..controllers import get_event_tickets_query
from . import main
from .forms import CreateEventForm, CreateTicketForm
from ..utils import flash_errors

@main.route('/event/<int:id>')
@login_required
def get_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    tickets = get_event_tickets_query(event_id=event.id).all()
    return render_template('events/event.html', event=event, tickets=tickets)

@main.route('/event')
@login_required
def get_events():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.order_by(Event.date.desc()).paginate(page, per_page=current_app.config['WEB_EVENTS_PER_PAGE'], error_out=False)
    events = pagination.items
    return render_template('events/events.html', events=events, pagination=pagination)

@main.route('/edit_event/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    form = CreateTicketForm()
    types = filter(lambda x: x[1] not in [ticket.type for ticket in event.tickets],
                   [(k, v) for (k, v) in enumerate(["Regular", "VVIP", "VIP"])])
    form.type.choices = types
    if form.validate_on_submit():
        ticket = Ticket(type=types[form.type.data][1], count=form.count.data, price=form.price.data)
        ticket.event_id = event.id
        db.session.add(ticket)
        db.session.commit()
        flash("Ticket added.", category="msg")
        return redirect(url_for(".get_event", id=event.id))
    else:
        flash_errors(form)
    return render_template('events/edit_event.html', form=form, event=event, tickets=event.tickets)

@main.route('/create_event', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = CreateEventForm()
    event = Event()
    if form.validate_on_submit():
        try:
            filename = photos.save(request.files['logo'])
            url = photos.url(filename)
            event.logo_url=url
        except:
            pass
        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        event.date = form.date.data

        db.session.add(event)
        db.session.commit()
        flash("Event {} created".format(event.title), category="msg")
        return redirect(url_for('.add_ticket', event_id=event.id))
    else:
        flash_errors(form)
    return render_template('events/create_event.html', event_form=form)

@main.route('/photos/<filename>')
def uploaded_image(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'photos'), filename)