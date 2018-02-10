#!/usr/bin/env python
"""
Launch script
Creates a shell context for the app
"""
import logging
import os

import click
from flask_migrate import Migrate
from sqlalchemy import null

from app import create_app, db
from app.model import User, Role, Account, Event, Package, Type, Ticket, Address, Code, AnonymousUser, Permission, \
    Message, Interval, Subscription, Campaign, Choice, Subscriber, Broadcast, Transaction

config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, User=User, Role=Role, Ticket=Ticket, Permission=Permission, AnonymousUser=AnonymousUser,
                Event=Event, Account=Account, Package=Package,
                Address=Address, Type=Type, Code=Code, Message=Message, Interval=Interval, Subscription=Subscription,
                Campaign=Campaign, Choice=Choice, Subscriber=Subscriber, Broadcast=Broadcast, Transaction=Transaction)



@app.cli.command()
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.model import Role, Type

    # migrate database to latest revision
    click.echo(click.style("Perfoming Migrations .....", fg='green'))
    upgrade()

    from app.deploy import insert_codes
    insert_codes.apply_async()

    # create user roles
    click.echo(click.style('Updating roles ....', fg='green'))
    Role.insert_roles()
    click.echo(click.style('Done ....', fg='green'))

    click.echo(click.style('adding ticket types ....', fg='green'))
    Type.insert_types()
    click.echo(click.style('Done ....', fg='green'))

    click.echo(click.style('adding address codes ....', fg='green'))
    Code.insert_codes()
    Interval.insert_intervals()
    click.echo(click.style('Done ....', fg='green'))

    users = User.query.filter(User.address_id.is_(None)).all()
    add = Address(city="Kampala")
    code = Code.by_country("Uganda")
    add.code = code
    add.save()
    for u in users:
        u.address = add
        u.save()
    return


@app.cli.command()
@click.option('--username', help='Username', prompt='Username', type=(str))
@click.option('--phonenumber', help='PhoneNumber', prompt='PhoneNumber', type=(str))
@click.password_option('--password', help='Admin Password', prompt=True, confirmation_prompt=True, hide_input=True, type=(str))
def superuser(username, phonenumber, password):
    """Creates a super-user Account
    """
    if not username or not phonenumber:
        click.echo(click.style('missing username', fg='red'))
        return
    role = Role.get_admin()
    user = User.query.filter_by(phone_number=phonenumber).first() or User.query.filter_by(username=username).first()
    user.role = role
    if user is not None:
        click.echo(click.style('phone number Already in Use', fg='red'))
        return
    user = User.create(username=username, password=password, phone_number=phonenumber)
    add = Address(city="Kampala")
    code = Code.by_country("Uganda")
    add.code = code
    user.address = add
    # commit I say Commit this changes
    user.save()
    click.echo(click.style('Super User created', fg='green'))
    # send mail

    return

COV = None
if os.environ.get('VALHALLA_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@app.cli.command()
def reset_db():
    """Resets and initialises db"""
    logging.info("Prepairing to reset db")
    db.session.commit()
    db.session.close_all()
    logging.info("Droping all Columns")
    db.drop_all()
    logging.info("Initializing new db")
    db.create_all()
    logging.info("DB reset")


from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropTable


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


@app.cli.command()
def test(coverage=False):
    """
    Run unit tests.
    :return: 
    """
    if coverage and not os.getenv('VALHALLA_COVERAGE'):
        import sys
        os.environ['VALHALLA_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        logging.info('Coverage Summary:')
        COV.report()
        # basedir = os.path.abspath(os.path.dirname(__file__))
        # covdir = os.path.join(basedir, 'tmp/coverage')
        # COV.html_report('HTML version: file://%s/index.html' % covdir)
        # COV.erase()
