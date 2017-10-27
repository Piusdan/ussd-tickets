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
from app.models import User, Role, Event, Ticket, Account, Location, Purchase

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
    return dict(app=app, User=User, Role=Role, Ticket=Ticket,
                Event=Event, Account=Account,
                Location=Location, db=db, Purchase=Purchase)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def reset_db():
    logging.info("Prepairing to reset db")
    db.session.commit()
    db.session.close_all()
    logging.info("Droping all Columns")
    db.drop_all()
    logging.info("Initializing new db")
    db.create_all()
    logging.info("Creating roles")
    Role.insert_roles()
    logging.info("DB reset")

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropTable


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


@manager.command
def add_roles():
    from flask_migrate import upgrade
    from app.models import Role

    # migrate db to latest version
    logging.info("migrating database to latest state")
    upgrade()

    # create user roles
    logging.info("adding user roles")
    Role.insert_roles()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.models import Role, User

    # migrate db to latest version
    upgrade()

    # create user roles
    Role.insert_roles()


@manager.command
def reset_db():
    logging.info("Prepairing to reset db")
    db.session.commit()
    db.session.close_all()
    logging.info("Droping all Columns")
    db.drop_all()
    logging.info("Initializing new db")
    db.create_all()
    logging.info("Creating roles")
    Role.insert_roles()
    logging.info("DB reset")

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropTable

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

@manager.command
def add_roles():
    from flask_migrate import upgrade
    from app.models import Role

    # migrate db to latest version
    logging.info("migrating database to latest state")
    upgrade()

    # create user roles
    logging.info("adding user roles")
    Role.insert_roles()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.models import Role, User

    # migrate db to latest version
    upgrade()

    # create user roles
    Role.insert_roles()


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


if __name__ == "__main__":
    manager.run()
