import base64
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

    html_content = f"""
    <html>
        <body>
            <pre>{text}</pre>
            <img src="data:image/png;base64,{img_data}" alt="Embedded Image" />
        </body>
    </html>
    """

    msg.set_content(text)
    msg.add_alternative(html_content, subtype="html")

    print(html_content)

    Vars.server.send_message(msg)
