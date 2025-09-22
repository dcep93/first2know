import base64
import smtplib
import sys
import time
import typing

from email.message import EmailMessage

from . import logger
from . import secrets


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def _build_server() -> smtplib.SMTP:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.login(
        secrets.Vars.secrets.email_user,
        secrets.Vars.secrets.email_password,
    )
    return server


def _get_pre(block: str) -> str:
    return f'<pre style="white-space:pre">{block}</pre>'


def send_text_email(email_to: str, subject: str, blocks: list[str]) -> None:
    msg = EmailMessage()
    msg["From"] = secrets.Vars.secrets.email_user
    msg["To"] = email_to
    msg["Subject"] = subject

    body = "\n".join([_get_pre(block) for block in blocks])

    html_content = f"""
    <html>
        <body>
            {body}
        </body>
    </html>
    """

    msg.set_content("\n".join(blocks))
    msg.add_alternative(html_content, subtype="html")

    try:
        with _build_server() as server:
            server.send_message(msg)
    except Exception as e:
        logger.log(f"email_wrapper.send_text_email {e}")
        sys.exit(1)


def send_img_email(
    email_to: str,
    subject: str,
    img_data: str,
    text: str,
) -> None:
    msg = EmailMessage()
    msg["From"] = secrets.Vars.secrets.email_user
    msg["To"] = email_to
    msg["Subject"] = subject

    img_cid = "embedded_image"

    html_content = f"""
    <html>
        <body>
            <img src="cid:{img_cid}" alt="Embedded Image">
            {_get_pre(text)}
            <div>{time.time()}</div>
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
        logger.log(f"email_wrapper.send_img_email {e}")
        sys.exit(1)
