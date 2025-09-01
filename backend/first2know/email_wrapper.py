import base64
import smtplib
import os
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

    img_cid = "embedded_image"

    html_content = f"""
    <html>
        <body>
            <img src="cid:{img_cid}" alt="Embedded Image">
            <pre>{text}</pre>
        </body>
    </html>
    """

    msg.set_content(text)
    msg.add_alternative(html_content, subtype="html")

    img_bytes = base64.b64decode(img_data)
    msg.get_payload()[1].add_related(  # type: ignore
        img_bytes, maintype="image", subtype="png", cid=img_cid
    )

    try:
        with _build_server() as server:
            server.send_message(msg)
    except Exception as e:
        print("email_wrapper.send_message", e)
        os.exit(1)
