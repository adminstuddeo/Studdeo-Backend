from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from aiosmtplib import SMTPException, send
from jinja2 import Template
from pydantic import BaseModel

from app.configuration import configuration
from app.enums import TemplateHTML


@dataclass
class EmailClient:
    email: str = configuration.EMAIL
    email_password: str = configuration.EMAIL_PASSWORD.get_secret_value()
    templates_directories: Path = Path(__file__).resolve().parent

    def _create_template_message(self, send_to: str, subject: str) -> EmailMessage:
        message: EmailMessage = EmailMessage()

        message["From"] = self.email
        message["To"] = send_to
        message["Subject"] = subject

        return message

    def _create_body_message(self, template_name: str) -> Template:
        with open(f"{self.templates_directories}/templates/{template_name}") as html:
            content: Template = Template(html.read())

        return content

    async def send_email(
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

        errors, response_code = await send(
            email_message,
            hostname=configuration.EMAIL_HOST,
            port=configuration.EMAIL_PORT,
            username=self.email,
            password=self.email_password,
            use_tls=True,
        )

        if errors or not response_code.startswith("2"):
            raise SMTPException("Failed to send email")
