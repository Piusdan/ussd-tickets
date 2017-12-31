from flask import render_template, flash, jsonify, request, redirect, url_for, abort
import logging
from flask_login import login_required
from app.main import main
from app.model import Interval, Message, Subscription, Campaign, Choice, Subscriber
from app.utils.web import flash_errors
import flask_excel as excel
from forms import CreateMessageForm, EditMessageForm, AddCampaignForm, EditCampaignForm, AddChoiceForm, EditChoiceForm


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


@main.route('/view-campaigns/<int:id>', methods=['get', 'post'])
@login_required
def campaign_details(id):
    campaign = Campaign.query.get(id)
    if campaign is None:
        abort(404)
    form = AddChoiceForm()
    if form.validate_on_submit():
        name = form.name.data
        keyword = form.keyword.data
        print name, keyword
        choice = Choice.create(name=name, keyword=keyword)
        campaign.choices.append(choice)
        campaign.save()
        flash("Choice Added")
        return redirect(url_for('.campaign_details', id=campaign.id))
    flash_errors(form)
    form.name.data = ''
    form.keyword.data = ''
    subscribers = Subscriber.query.join(Choice).filter(Choice.campaign_id==campaign.id)
    choices = campaign.choices
    return render_template('/sms/campaign_details.html', form=form, campaign=campaign, subscribers=subscribers, choices=choices)


@main.route('/delete-campaigns/<int:id>')
@login_required
def delete_campaign(id):
    campaign = Campaign.query.get(id)
    if campaign is None:
        abort(404)
    campaign.delete()
    flash('Campaign Deleted')
    return redirect(url_for('.sms_campaigns'))

@main.route('/view-choice/<string:keyword>')
@login_required
def choice_details(keyword):
    choice = Choice.query.filter_by(keyword=keyword).first_or_404()
    return render_template('/sms/choice_details.html', choice=choice)


@main.route('/sms/incoming-message', methods=['post', 'get'])
def sms_incoming_message():
    """Receives sms callbacks from the user & saves message to the database
    :param from: The number that sent the message
    :param to: The number to which the message was sent
    :param text: The message content
    :param date: The date and time when the message was received
    :param id: The internal ID that we use to store this message
    :param linkId: Optional parameter required when responding to an on-demand user request with a premium message
    """
    from_ = request.values.get('from')
    to_ = request.values.get('to')
    text = request.values.get('text')
    id_ = request.values.get('id')
    linkId = request.values.get('linkId')
    # record message
    text = text.strip()
    choice = Choice.query.filter_by(keyword=text).first()
    if choice is not None:
        subs = Subscriber.query.join(Choice).filter_by()
        subs = Subscriber.create(phone_number=from_)
        subs.choice_id = choice.id
        subs.save()
    return jsonify('Received Message'), 200

