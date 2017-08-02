from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from ..models import User, Event, Ticket
from . import main



@main.route('/')
@login_required
def index():
    return redirect(url_for('main.get_events'))

@main.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    tickets = Ticket.query.all()
    events = Event.query.all()

    context = {
        "users": users,
        "events": events,
        "tickets": tickets,
        "total_users": len(users),
        "total_tickets": len(tickets),
        "total_events": len(events)
    }

    return render_template('main/dashboard.html', context=context)
