import os
import sys
import click
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import User
from ml.train_model import train_and_evaluate

env_mode = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_mode)


@app.cli.command("init-db")
def init_db():
    """Initializes the database schema."""
    db.create_all()
    click.echo("[+] Database tables initialized successfully.")


@app.cli.command("create-admin")
@click.option('--email', prompt='Admin email address', help='Email for the administrator account.')
@click.option('--name', prompt='Admin full name', default='Administrator', help='Full name for administrator.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for administrator.')
def create_admin(email, name, password):
    """Securely creates or upgrades an administrator account."""
    normalized_email = email.strip().lower()
    user = User.query.filter(User.email.ilike(normalized_email)).first()

    if user:
        if user.is_admin:
            click.echo(f"[!] User {normalized_email} is already an administrator.")
            return
        user.role = 'admin'
        user.set_password(password)
        db.session.commit()
        click.echo(f"[+] Existing user {normalized_email} upgraded to administrator role.")
    else:
        new_admin = User(
            full_name=name.strip(),
            email=normalized_email,
            role='admin'
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f"[+] Administrator account '{normalized_email}' created successfully.")


@app.cli.command("train-ml")
@click.option('--dataset', default=None, help='Path to custom labeled CSV dataset.')
def train_ml(dataset):
    """Runs the machine learning training pipeline."""
    click.echo("[*] Starting model training...")
    report = train_and_evaluate(dataset_csv=dataset)
    click.echo(f"[+] Model training completed. Test accuracy: {report['metrics']['accuracy']*100:.2f}%")


if __name__ == '__main__':
    # Support command line flag parsing for direct execution
    if len(sys.argv) > 1 and sys.argv[1] == 'create-admin':
        with app.app_context():
            import argparse
            parser = argparse.ArgumentParser(description="Create Administrator Account")
            parser.add_argument('--email', required=True, help="Admin email")
            parser.add_argument('--name', default="Administrator", help="Admin name")
            parser.add_argument('--password', required=True, help="Admin password")
            # Parse args skipping the 'create-admin' verb
            parsed, _ = parser.parse_known_args(sys.argv[2:])
            
            norm_email = parsed.email.strip().lower()
            existing = User.query.filter(User.email.ilike(norm_email)).first()
            if existing:
                existing.role = 'admin'
                existing.set_password(parsed.password)
                db.session.commit()
                print(f"[+] Existing user {norm_email} updated to administrator.")
            else:
                admin_user = User(
                    full_name=parsed.name.strip(),
                    email=norm_email,
                    role='admin'
                )
                admin_user.set_password(parsed.password)
                db.session.add(admin_user)
                db.session.commit()
                print(f"[+] Administrator {norm_email} created successfully.")
            sys.exit(0)

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    print("==================================================")
    print(" Fake Job & Internship Detection System Starting ")
    print(f" URL: http://127.0.0.1:{port}")
    print("==================================================")
    app.run(host='127.0.0.1', port=port, debug=debug)

