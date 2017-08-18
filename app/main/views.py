from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from ..models import User, Event, Ticket, Purchase
from . import main



@main.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
    users = len(User.query.all())
    tickets = len(Ticket.query.all())
    purchases = len(Purchase.query.all())
    events = len(Event.query.all())
    campaigns = 0

    context = {
        "users": users,
        "events": events,
        "tickets": tickets,
        "purchases": purchases,
        "campaigns": campaigns
    }

    return render_template('main/dashboard.html', context=context)
