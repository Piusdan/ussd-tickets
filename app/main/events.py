import os
import datetime
import logging
from flask import render_template,flash,redirect,url_for,request,send_from_directory,current_app, jsonify, abort
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.model import Event, Type, Ticket, Package, Address
from app import db
from app.utils.web import eastafrican_time
from app.main import main
from app.main.forms import CreateEventForm, CreatePackageForm, EditEventForm, EditPackageForm


@main.route('/event/<string:slug>', methods=['POST', 'GET'])
@login_required
@admin_required
def get_event(slug):
    package_form = CreatePackageForm()

    event = Event.by_slug(slug)
    packages = Event.packages
    tickets = db.session.query(Package.price).join(Ticket).filter(Package.event == event)
    total_sales = 0
    daily_sales = 0
    for price in tickets.all():
        total_sales += price[0]
    today = eastafrican_time().date()
    yesterday = eastafrican_time() + datetime.timedelta(days=1)
    todays_tickets = tickets.filter(Ticket.created_at.between(today, yesterday.date()))
    for price in todays_tickets.all():
        daily_sales += price[0]
    return render_template('events/event.html',
                           event=event,
                            packages=packages,
                           package_form=package_form,
                           total_sales=total_sales,
                           daily_sales=daily_sales)


@main.route('/event', methods=['POST', 'GET'])
@login_required
def get_events():
    events = db.session.query(Event).order_by(Event.date).all()
    event_form = CreateEventForm()
    return render_template('events/events.html', events=events, event_form=event_form)

@main.route('/event/edit/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_event(slug):
    event = Event.by_slug(slug)
    if event is None:
        abort(404)
    packages = event.packages.join(Type).filter(~Type.name.in_(['Organiser'])).all()
    event_type_names = db.session.query(Type.name).join(Package).filter(Package.event_id==event.id).all()
    create_packageForm = CreatePackageForm()
    # TODO don't display organiser already created event
    none_event_types = db.session.query(Type).filter(~Type.name.in_(event_type_names)).all()
    create_packageForm.type.choices = [(type.id, type.name) for type in none_event_types]

    edit_packageForm = EditPackageForm()
    edit_eventForm = EditEventForm()
    edit_eventForm.title.data = event.name
    edit_eventForm.description.data = event.description
    edit_eventForm.location.data = event.address.city
    edit_eventForm.venue.data = event.address.location
    edit_eventForm.date.data = event.date
    logging.warning("none event types {}".format(none_event_types))
    return render_template('events/edit.html',
                           edit_eventForm=edit_eventForm,
                           edit_packageForm=edit_packageForm,
                           create_packageForm=create_packageForm,
                           event=event,
                           tickets='',
                           packages=packages,
                           none_event_types=none_event_types)


@main.route('/event/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_event(id):
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    event_date = request_dict["date"]
    event = Event.query.get(id)
    logging.info(type(id))
    if event is None:
        abort(404)
    event.date = datetime.datetime.strptime(event_date, '%d/%m/%Y').date()
    event.name = request_dict["title"]
    event.description = request_dict["description"]
    event.organiser_id = current_user.id
    event.address.city = request_dict["location"]
    event.address.location = request_dict["venue"]
    logging.info(data)
    event.save()
    response = jsonify(dict(data="Event {} edited".format(event.name)))
    response.status_code = 201
    logging.info(response)
    return response


@main.route('/event/create', methods=['POST', 'GET'])
@login_required
@admin_required
def add_event():
    data = request.get_json()
    request_dict = {}
    map(lambda x: request_dict.setdefault(x.get('name'), x.get('value')), data)
    date = datetime.datetime.strptime(request_dict["date"], '%d/%m/%Y').date()
    name = request_dict["title"]
    description = request_dict["description"]
    event = Event.create(name=name, description=description, date=date)
    # TODO add organiser ticket
    organiser = Package.create(event_id=event.id, type=Type.by_name('Organiser'), price=0.00)
    Ticket.create(package_id=organiser.id, user_id=current_user.id)
    logging.info(data)
    city = request_dict["location"]
    venue = request_dict["venue"]
    event.address = Address.create(city=city, location=venue)
    event.save()
    response = jsonify(dict(data="Event {} created".format(event.name)))
    response.status_code = 201
    return response


@main.route('/delete/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.by_id(id)
    payload = {"event_id": event_id}
    event.delete()
    flash('{} deleted!'.format(event.title), category='message')
    return redirect(url_for('.get_events'))


@main.route('/photos/<filename>')
def uploaded_image(filename):
    return send_from_directory(
        os.path.join(
            current_app.config['UPLOADS_DEFAULT_DEST'],
            'photos'), filename)
