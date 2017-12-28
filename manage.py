#!/usr/bin/env python
"""
Launch script
Creates a shell context for the app
"""
import os
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate
import logging

from app import create_app, db
from app.model import User, Role, Account, Event, Package, Type, Ticket, Address, Code, AnonymousUser, Permission, Message, Interval, Subscription

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)
manager = Manager(app)

logging.info("initialising app")

COV = None

if os.environ.get('VALHALLA_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


def make_shell_context():
    return dict(app=app, User=User, Role=Role, Ticket=Ticket,Permission=Permission,AnonymousUser=AnonymousUser,
                Event=Event, Account=Account, Package=Package,
                Address=Address, Type=Type, Code=Code, Message=Message, Interval=Interval, Subscription=Subscription)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
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


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.model import Role, Type

    # migrate db to latest version
    logging.info("migrating database to latest state")
    upgrade()

    from app.deploy import insert_codes
    insert_codes.apply_async()
    # create user roles
    logging.info("adding user roles")
    Role.insert_roles()
    # create user roles
    logging.info("adding ticket types")
    Type.insert_types()
    Code.insert_codes()

    Interval.insert_intervals()


@manager.command
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
