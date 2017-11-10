import logging

from flask import make_response

from app.model import Package, Ticket, User, Event
from app.ussd.session import expire_session


def respond(menu_text, session_id=None, pretext=True, preformat=True):
    """
    :param menu_text: menu text to display
    :param pretext: set to False if you don't want to include a predifined header
    :param session_id: include this if you wish to stop tracking the user journey :Depreciated
    :return: a ussd response 
    """
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def paginate_events(session, menu_text):
    page = session.get('page')  # get page for pagination purposes
    if page is None or page < 1:  # first iteration page is not set, initialise it to 1
        page = 1
    pagination = Event.query.order_by(Event.date).paginate(page, 5, False)  # get events in groups of 5
    events = pagination.items
    if events:
        events_displayed = {}  # a mapping of events to the displayed number used to track displayed events
        for index, event in enumerate(events):
            index += 1
            menu_text += "{num}. {event_name}\n".format(num=index, event_name=event.name)
            events_displayed[index] = event.slug  # Track displayed number and event slug
        logging.warn(events_displayed)
        session['displayed_events'] = events_displayed  # add to session tracker

        if pagination.has_next:
            # update session to level 3
            session['page'] = page + 1
            menu_text += "98. More"
        if pagination.has_prev:
            menu_text += "0. Back"
    return session, menu_text