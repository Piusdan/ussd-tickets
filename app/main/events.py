import os

from flask import (render_template,
                   abort,
                   flash,
                   redirect,
                   url_for,
                   request,
                   send_from_directory,
                   current_app)

from flask_login import login_required

from app.decorators import admin_required
from app.models import Event, Ticket
from app import photos, db
from app.main.utils import create_event as new_event
from app.controllers import (get_event_tickets_query,
                           edit_event,
                           async_delete_event,
                           get_event_attendees_query)
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
    ticket_forms = []
    for ticket in tickets:
        edit_ticket_form = EditTicketForm(ticket)
        edit_ticket_form.count.data = ticket.count
        edit_ticket_form.price.data = ticket.price
        ticket_forms.append(edit_ticket_form)


    # validate ticket form
    if ticket_form.validate_on_submit():
        ticket = Ticket(type=types[ticket_form.type.data],
                        count=ticket_form.count.data, price=ticket_form.price.data)
        ticket.event = event
        db.session.add(ticket)
        flash("Ticket added.", category="success")
        db.session.commit()
        return redirect(url_for('.get_event', id=event.id))
    else:
        flash_errors(ticket_form)

    # initialise validate event form
    event_form = EditEventForm()
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
        flash("Edited {}".format(event.title), category="success")
        return redirect(url_for('.get_event', id=event.id))
    else:
        flash_errors(event_form)
    event_form.title.data = event.name
    event_form.description.data = event.description
    event_form.location.data = event.city
    event_form.venue.data = event.venue
    event_form.date.data = event.date

    return render_template('events/event.html', event=event, tickets=tickets,
                           event_form=event_form,
                           purchases=attendees,
                           ticket_form=ticket_form,
                           edit_ticket_forms=ticket_forms)


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
