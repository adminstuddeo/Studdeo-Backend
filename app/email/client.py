import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from jinja2 import Template
from pydantic import BaseModel

from app.configuration import configuration
from app.enums import TemplateHTML

SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.send"]


class EmailClient:
    def __init__(self) -> None:
        self.email: str = configuration.EMAIL
        self.templates_directories: Path = Path(__file__).resolve().parent

    def _create_template_message(self, send_to: str, subject: str) -> EmailMessage:
        message: EmailMessage = EmailMessage()

        message["From"] = self.email
        message["To"] = send_to
        message["Subject"] = subject

        return message

    def _get_credential(self) -> Credentials:
        return Credentials("credentials.json", SCOPES)

    def _create_body_message(self, template_name: str) -> Template:
        with open(f"{self.templates_directories}/templates/{template_name}") as html:
            content: Template = Template(html.read())

        return content

    def _encode_message(self, message: EmailMessage) -> Dict[str, Any]:
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        return {"raw": raw}

    def send_email(
        self,
        subject: str,
        email: str,
        email_information: BaseModel,
        template_name: TemplateHTML,
    ) -> None:
        credentials: Credentials = self._get_credential()

        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

        email_template: Template = self._create_body_message(
            template_name=template_name
        )

        email_message: EmailMessage = self._create_template_message(
            send_to=email, subject=subject
        )

        content: str = email_template.render(email_information.model_dump())

        email_message.add_alternative(content, subtype="html")

        body: Dict[str, Any] = self._encode_message(message=email_message)

        service.users().messages().send(userId="me", body=body).execute()
