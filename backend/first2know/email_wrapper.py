import smtplib
import typing
from email.message import EmailMessage

from . import secrets


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def _build_server():
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.login(
        secrets.Vars.secrets.email_user,
        secrets.Vars.secrets.email_password,
    )
    return server


class Vars:
    server = _build_server()


def send_email(
    email_to: str,
    subject: str,
    text: str,
    img_data: str,
):
    msg = EmailMessage()
    msg["From"] = secrets.Vars.secrets.email_user
    msg["To"] = email_to
    msg["Subject"] = subject

    print(msg, text, img_data)

    Vars.server.send_message(msg)
