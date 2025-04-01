# -*- coding: utf-8 -*-
"""Click commands."""

import click
from flask.cli import with_appcontext, AppGroup
from flask_security.utils import hash_password
from rich.console import Console
import secrets
import string
import os

from enferno.extensions import db
from enferno.user.models import User
from enferno.agents import DeveloperAgent

console = Console()

# Create agent command group
agent_cli = AppGroup('agent', help='AI-powered development tools for Enferno framework')

@agent_cli.command('template')
@click.argument('request', required=False)
@click.option('--template-path', default='index.html', help='Path to the template file')
@with_appcontext
def template_cmd(request, template_path):
    """Modify a template using AI assistance."""
    if not request:
        request = click.prompt('What changes would you like to make to the template?')
    
    try:
        agent = DeveloperAgent()
        agent.modify_template(request, template_path)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@click.command()
@with_appcontext
def create_db():
    """creates db tables - import your models within commands.py to create the models.
    """
    db.create_all()
    print('Database structure created successfully')


@click.command()
@with_appcontext
def install():
    """Install a default admin user and add an admin role to it.
    """
    # check if admin exists
    from enferno.user.models import Role
    # create admin role if it doesn't exist
    admin_role = Role.query.filter(Role.name == 'admin').first()
    if not admin_role:
        admin_role = Role(name='admin').save()

    # check if admin users already installed
    admin_user = User.query.filter(User.roles.any(Role.name == 'admin')).first()
    if admin_user:
        console.print(f"[yellow]An admin user already exists:[/] [blue]{admin_user.username}[/]")
        return

    # else : create a new admin user
    username = click.prompt('Admin username', default='admin')
    # Generate a secure password
    password = ''.join(secrets.choice(string.ascii_letters + string.digits + '@#$%^&*') for _ in range(32))

    user = User(username=username, name='Super Admin', password=hash_password(password), active=1)
    user.roles.append(admin_role)
    user.save()
    
    console.print("\n[green]✓[/] Admin user created successfully!")
    console.print(f"[blue]Username:[/] {username}")
    console.print(f"[blue]Password:[/] [red]{password}[/]")
    console.print("\n[yellow]⚠️  Please save this password securely - you will not see it again![/]")


@click.command()
@click.option('-e', '--email', prompt=True, default=None)
@click.option('-p', '--password', prompt=True, default=None)
@with_appcontext
def create(email, password):
    """Creates a user using an email.
    """
    a = User.query.filter(User.email == email).first()
    if a != None:
        print('User already exists!')
    else:
        user = User(email=email, password=hash_password(password), active=True)
        user.save()


@click.command()
@click.option('-e', '--email', prompt=True, default=None)
@click.option('-r', '--role', prompt=True, default='admin')
@with_appcontext
def add_role(email, role):
    """Adds a role to the specified user.
        """
    from enferno.user.models import Role
    u = User.query.filter(User.email == email).first()

    if u is None:
        print('Sorry, this user does not exist!')
    else:
        r = db.session.execute(db.select(Role).filter_by(name=role)).scalar_one()
        if r is None:
            print('Sorry, this role does not exist!')
            u = click.prompt('Would you like to create one? Y/N', default='N')
            if u.lower() == 'y':
                r = Role(name=role)
                try:
                    db.session.add(r)
                    db.session.commit()
                    print('Role created successfully, you may add it now to the user')
                except Exception as e:
                    db.session.rollback()
        # add role to user
        u.roles.append(r)


@click.command()
@click.option('-e', '--email', prompt='Email or username', default=None)
@click.option('-p', '--password', hide_input=True, prompt=True, default=None)
@with_appcontext
def reset(email, password):
    """Reset a user password using email or username
    """
    try:
        pwd = hash_password(password)
        # Check if user exists with provided email or username
        u = User.query.filter((User.email == email) | (User.username == email)).first()
        if not u:
            print(f'User with email or username "{email}" not found.')
            return
        
        u.password = pwd
        try:
            db.session.commit()
            print('User password has been reset successfully.')
        except:
            db.session.rollback()
            print('Error committing to database.')
    except Exception as e:
        print('Error resetting user password: %s' % e)


i18n_cli = AppGroup('i18n')


@i18n_cli.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language"""
    if os.system("pybabel init -i messages.pot -d enferno/translations -l " + lang):
        raise RuntimeError("init command failed")


@i18n_cli.command()
def extract():
    """Extract messages from code"""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("Extract command failed")


@i18n_cli.command()
def update():
    """Update translations"""
    if os.system("pybabel update -i messages.pot -d enferno/translations"):
        raise RuntimeError("Update command failed")


@i18n_cli.command()
def compile():
    """Compile translations"""
    if os.system("pybabel compile -d enferno/translations"):
        raise RuntimeError("Compile command failed")