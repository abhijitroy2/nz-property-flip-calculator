import mimetypes
import os
import smtplib
from email.message import EmailMessage
from typing import List

from .config import EmailConfig


def send_email(cfg: EmailConfig, subject: str, body: str, attachments: List[str]) -> None:
    if not cfg.enabled or not cfg.recipients:
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg.username
    msg["To"] = ", ".join(cfg.recipients)
    msg.set_content(body)

    for path in attachments:
        if not os.path.exists(path):
            continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
        server.starttls()
        if cfg.username and cfg.password:
            server.login(cfg.username, cfg.password)
        server.send_message(msg)


