import os
import datetime
import logging
from flask import render_template,flash,redirect,url_for,request,send_from_directory,current_app, jsonify, abort
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import Event
from app import photos, db
from app.main.utils import get_country, create_event as new_event
from app.controllers import get_event_tickets_query,edit_event, async_delete_event, get_event_attendees_query
from app.main import main
from app.main.forms import CreateEventForm, CreateTicketForm, EditEventForm, EditTicketForm
from app.common.utils import flash_errors



@main.route('/event/<int:id>', methods=['POST', 'GET'])
@login_required
def get_event(id):
    ticket_form = CreateTicketForm()

    event = Event.query.filter_by(id=id).first_or_404()

    tickets = get_event_tickets_query(event_id=event.id).all()

    attendees = get_event_attendees_query(event.id).all()

    # # update ticket type select field
    ticket_form.type.choices = filter(lambda x: x[1] not in
                                      [ticket.type for ticket in event.tickets],
                                      [(k, v) for (k, v) in enumerate(
                                          current_app.config['TICKET_TYPES'])])

    # list of all ticket types
    types = current_app.config['TICKET_TYPES']

    # to help us edit tickets
    edit_ticket_form = EditTicketForm()
    # initialise validate event form
    event_form = EditEventForm()
    if ticket_form.validate_on_submit():
        pass
        flash("hell yeah")
    if event_form.validate_on_submit():
        try:
            filename = photos.save(request.files['logo'])
            url = photos.url(filename)
        except:
            url = event.logo_url
        payload = {
            "event_id": event.id,
            "logo_url": url,
            "title": event_form.title.data,
            "description": event_form.description.data,
            "location": event_form.location.data,
                "date": event_form.date.data,
                "venue": event_form.venue.data
            }
        edit_event.apply_async(args=[payload], countdown=0)
        db.session.commit()
        flash("Edited {}".format(event_form.title.data), category="success")
        return redirect(url_for('.get_event', id=event.id))
    else:
        flash_errors(event_form)
    event_form.title.data = event.name
    event_form.description.data = event.description
    event_form.location.data = event.city
    event_form.venue.data = event.venue
    event_form.date.data = event.date

    return render_template('events/event.html',
                           event=event,
                           tickets=tickets,
                           event_form=event_form,
                           purchases=attendees,
                           ticket_form=ticket_form,
                           edit_ticket_form=edit_ticket_form)


@main.route('/event', methods=['POST', 'GET'])
@login_required
def get_events():
    events = Event.query.all()
    event_form = CreateEventForm()
    return render_template('events/events.html', events=events, event_form=event_form)


@main.route('/event/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get(id)
    if event is None:
        abort(404)
    tickets = event.tickets
    create_ticketForm = CreateTicketForm()
    # # update ticket type select field
    create_ticketForm.type.choices = filter(lambda x: x[1] not in
                                      [ticket.type for ticket in event.tickets],
                                      [(k, v) for (k, v) in enumerate(
                                          current_app.config['TICKET_TYPES'])])
    edit_ticketForm = EditTicketForm()
    edit_eventForm = EditEventForm()
    edit_eventForm.title.data = event.name
    edit_eventForm.description.data = event.description
    edit_eventForm.location.data = event.city
    edit_eventForm.venue.data = event.venue
    edit_eventForm.date.data = event.date
    return render_template('events/edit.html',
                           edit_eventForm=edit_eventForm,
                           edit_ticketForm=edit_ticketForm,
                           event=event,
                           tickets=tickets)


@main.route('/event/create', methods=['POST', 'GET'])
@login_required
@admin_required
def add_event():
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    event_date = request_dict["date"]
    event = Event()
    event.venue = request_dict["venue"]
    event.date = datetime.datetime.strptime(event_date, '%d/%m/%y').date()
    event.name = request_dict["title"]
    event.city = request_dict["location"]
    event.description = request_dict["description"]
    event.organiser_id = current_user.id
    country = get_country(event.city)
    logging.info(data)
    try:
        if country is None:
            raise Exception
        event.country = country
    except Exception as exc:
        response = jsonify(dict(data="Error:Please enter  a valid location/city/town"))
        response.status_code = 400
        return response

    db.session.add(event)
    db.session.commit()
    response = jsonify(dict(data="Event {} created".format(event.name)))
    response.status_code = 201

    return response


@main.route('/delete/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    payload = {"event_id": event_id}
    async_delete_event.apply_async(args=[payload], countdown=0)
    flash('{} deleted!'.format(event.title), category='message')
    return redirect(url_for('.get_events'))


@main.route('/create_event', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = CreateEventForm()
    filename = ""
    if form.validate_on_submit():
        try:
            filename = photos.save(request.files['logo'])
            filename = filename
        except:
            pass
        payload = {
            "filename": filename,
            "name": form.title.data,
            "description": form.description.data,
            "location": form.location.data,
            "date": form.date.data,
            "venue": form.venue.data
        }

        event = new_event(payload)
        flash("Event {} created".format(event.name), category="msg")
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
