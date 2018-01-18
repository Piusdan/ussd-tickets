from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.model import User, Event, Ticket, Package
from . import main

@main.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
    users = User.query.count()
    tickets = Ticket.query.count()
    events = Event.query.count()
    campaigns = 0

    context = {
        "users": users,
        "events": events,
        "tickets": tickets,
        "campaigns": campaigns
    }

    return render_template('main/dashboard.html', context=context)
