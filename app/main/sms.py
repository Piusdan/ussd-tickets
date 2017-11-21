from flask import render_template, flash, jsonify, request, redirect, url_for
import logging
from flask_login import login_required
from app.main import main
from app.model import Interval, Message, Subscription
from app.utils.web import flash_errors
import flask_excel as excel
from forms import CreateMessageForm


@main.route('/sms', methods=['post', 'get'])
@login_required
def bulk_sms():
    form = CreateMessageForm()
    messages = Message.query.all()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        start = form.startdate.data
        end = form.enddate.data
        interval_id = form.interval.data
        message = Message.create(body=body,title=title, expiry=end, interval_id=interval_id )
        subscription_array = request.get_records(field_name='subscriptions')
        for value in subscription_array:
            phone_number = value.get('phone_number') or value.get('Phone Number') or value.get('phone number')
            phone_number = '+256{}'.format(str(phone_number)[-9:])
            subscription = Subscription.create(phone_number=phone_number)
            message.subscriptions.append(subscription)
        message.save()
        flash(message="Form submitted", category='success')
        return redirect(url_for('.bulk_sms'))
    else:
        flash_errors(form)
    return render_template("sms/sms.html", form=form, messages=messages)
