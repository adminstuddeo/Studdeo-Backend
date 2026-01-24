import base64
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build  # type:ignore
from jinja2 import Template
from pydantic import BaseModel

from app.configuration import configuration
from app.enums import TemplateHTML


@dataclass
class EmailClient:
    email: str = configuration.EMAIL
    token_path: Path = Path("/tmp/gmail_token.json")
    templates_directories: Path = Path(__file__).resolve().parent
    service: Resource = field(init=False)

    def __post_init__(self) -> None:
        if not self.token_path.exists():
            decoded_data = base64.b64decode(configuration.GMAIL_TOKEN_JSON).decode(
                "utf-8"
            )
            self.token_path.write_text(decoded_data, encoding="utf-8")

        self.service = self._build_service()

    def _build_service(self) -> Resource:
        creds: Credentials = Credentials.from_authorized_user_file(
            filename=self.token_path,
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(request=Request())

        return build("gmail", "v1", credentials=creds)

    def _create_template_message(self, send_to: str, subject: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.email
        message["To"] = send_to
        message["Subject"] = subject

        return message

    def _create_body_message(self, template_name: TemplateHTML) -> Template:
        with open(
            file=f"{self.templates_directories}/templates/{template_name.value}"
        ) as html:
            return Template(html.read())

    def send_email(
        self,
        subject: str,
        email: str,
        email_information: BaseModel,
        template_name: TemplateHTML,
    ) -> None:
        email_template: Template = self._create_body_message(
            template_name=template_name
        )

        email_message: EmailMessage = self._create_template_message(
            send_to=email, subject=subject
        )

        content: str = email_template.render(email_information.model_dump())

        email_message.add_alternative(content, subtype="html")

        raw_message: str = base64.urlsafe_b64encode(email_message.as_bytes()).decode()

        self.service.users().messages().send(
            userId="me",
            body={"raw": raw_message},
        ).execute()
