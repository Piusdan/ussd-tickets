from flask import render_template, flash, jsonify, request, redirect, url_for
import logging
from flask_login import login_required
from app.main import main
from app.model import Interval, Message, Subscription, Campaign, Choice, Subscriber
from app.utils.web import flash_errors
import flask_excel as excel
from forms import CreateMessageForm, EditMessageForm, AddCampaignForm, EditCampaignForm, AddChoiceForm


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

@main.route('/sms/<string:slug>/details')
@login_required
def sms_details(slug):
    message = Message.query.filter_by(slug=slug).first_or_404()
    broadcasts = message.broadcasts
    return render_template('sms/details.html', message=message, broadcasts=broadcasts)

@main.route('/sms/<string:slug>/edit-details', methods=['get','post'])
@login_required
def edit_bulk_sms(slug):
    message = Message.query.filter_by(slug=slug).first_or_404()
    form = EditMessageForm(message)
    if form.validate_on_submit():
        message.title = form.title.data
        message.body = form.body.data
        message.expiry = form.enddate.data
        message.interval_id = form.interval.data
        try:
            subscription_array = request.get_records(field_name='subscriptions')
            for value in subscription_array:
                phone_number = value.get('phone_number') or value.get('Phone Number') or value.get('phone number')
                phone_number = '+256{}'.format(str(phone_number)[-9:])
                subscription = Subscription.create(phone_number=phone_number)
                message.subscriptions.append(subscription)
        except IOError as exc:
            pass
        message.save()
        flash(message="SMS Details Updated", category='success')
        return redirect(url_for('.sms_details', slug=message.slug))
    else:
        flash_errors(form)
    form.title.data = message.title
    form.body.data = message.body
    form.enddate.data = message.expiry
    form.interval.data = message.interval_id
    return render_template('sms/edit.html', message=message, form=form)

@main.route('/sms/<string:slug>/delete')
@login_required
def delete_bulk_sms(slug):
    message = Message.query.filter_by(slug=slug).first_or_404()
    message.delete()
    flash("Broadcast removed", category="warning")
    return redirect(url_for('.bulk_sms'))

@main.route('/campaigns', methods=['get','post'])
@login_required
def sms_campaigns():
    form = AddCampaignForm()
    campaigns = Campaign.query.all()
    if form.validate_on_submit():
        title = form.title.data
        expiry = form.expiry.data
        campaign = Campaign.create(title=title, expiry=expiry)
        flash(message="New SMS Campaign Added")
        return redirect(url_for('.sms_campaigns'))
    form.title.data = ''
    form.expiry.data = ''
    return render_template('/sms/campaigns.html', campaigns=campaigns, form=form)


@main.route('/campaigns/<string:slug>')
@login_required
def campaign_details(slug):
    campaign = Campaign.by_slug(slug)
    form = AddChoiceForm()
    subscribers = Subscriber.query.join(Choice).filter(Choice.campaign_id==campaign.id).all()
    return render_template('/sms/campaigns_details.html', form=form, campaign=campaign, subscribers=subscribers)