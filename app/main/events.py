import os
from flask import render_template, abort, flash, redirect, url_for, request, send_from_directory, current_app

from flask_login import login_required, current_user
from ..decorators import admin_required
from ..models import User, Event, Ticket, Account, Location
from .. import photos, db
from ..controllers import get_event_tickets_query, edit_event, new_event, async_delete_event, get_event_attendees_query
from . import main
from .forms import CreateEventForm, CreateTicketForm, EditEventForm
from ..utils import flash_errors


@main.route('/event/<int:id>', methods=['POST', 'GET'])
@login_required
def get_event(id):
    form = EditEventForm()
    event = Event.query.filter_by(id=id).first_or_404()
    tickets = get_event_tickets_query(event_id=event.id).all()
    if form.validate_on_submit():
        try:
            filename = photos.save(request.files['logo'])
            url = photos.url(filename)
        except:
            url = event.logo_url

        payload = {
            "event_id": event.id,
            "logo_url": url,
            "title": form.title.data,
            "description": form.description.data,
            "location": form.location.data,
            "date": form.date.data,
            "venue": form.venue.data
        }
        edit_event.apply_async(args=[payload], countdown=0)
        flash("Eidited {}".format(event.title), category="msg")
        return redirect(url_for('.get_event', id=event.id))

    else:
        flash_errors(form)
    form.title.data = event.title
    form.description.data = event.description
    form.location.data = event.location
    form.venue.data = event.venue
    form.date.data = event.date
    return render_template('events/event.html', event=event, tickets=tickets, form=form)


@main.route('/event')
@login_required
def get_events():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.order_by(Event.date.desc()).paginate(
        page, per_page=current_app.config['WEB_EVENTS_PER_PAGE'], error_out=False)
    events = pagination.items
    return render_template('events/events.html', events=events, pagination=pagination)


@main.route('/delete/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    payload = {"event_id": event_id}
    async_delete_event.apply_async(args=[payload], countdown=0)
    flash('{} deleted!'.format(event.title))
    return redirect(url_for('.get_events'))


@main.route('/create_event', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = CreateEventForm()
    url = ""
    if form.validate_on_submit():
        try:
            filename = photos.save(request.files['logo'])
            url = photos.url(filename)
        except:
            pass
        payload = {
            "logo_url": url,
            "title": form.title.data,
            "description": form.description.data,
            "location": form.location.data,
            "date": form.date.data,
            "venue": form.venue.data
        }

        event = new_event(payload)
        flash("Event {} created".format(event.title), category="msg")
        return redirect(url_for('.get_event', id=event.id))
    else:
        flash_errors(form)
    return render_template('events/create_event.html', event_form=form)


@main.route('/photos/<filename>')
def uploaded_image(filename):
    return send_from_directory(
        os.path.join(
            current_app.config['UPLOADS_DEFAULT_DEST'],
            'photos'), filename)


@main.route('/details/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def event_details(event_id):
    page = request.args.get('page', 1, type=int)
    event = Event.query.filter_by(id=event_id).first()
    # pagination = get_event_attendees_query(event_id).paginate(page, per_page=10, error_out=False)
    attendees = get_event_attendees_query(event_id).all()
    # pagination = filter(lambda att: att.ticket.event_id==event_id, attendees)
    # attendees = pagination.items

    # count = len(attendees)
    # total = pagination.total
    return render_template('events/event_details.html', event=event, purchases=attendees)
