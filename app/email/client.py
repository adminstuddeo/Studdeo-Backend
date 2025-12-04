from email.message import EmailMessage
from pathlib import Path
from string import Template

from aiosmtplib import send
from aiosmtplib.errors import SMTPException
from pydantic import BaseModel

from app.configuration import configuration
from app.enums import TemplateHTML


class EmailClient:
    def __init__(self) -> None:
        self.stmp_host: str = configuration.EMAIL_HOST
        self.smtp_port: int = configuration.EMAIL_PORT
        self.email: str = configuration.EMAIL
        self.password: str = configuration.EMAIL_PASSWORD.get_secret_value()
        self.templates_directories: Path = Path(__file__).resolve().parent

    def _create_template_message(self, send_to: str, subject: str) -> EmailMessage:
        message: EmailMessage = EmailMessage()

        message["From"] = self.email
        message["To"] = send_to
        message["Subject"] = subject

        return message

    def _create_body_message(self, template_name: str) -> Template:
        with open(f"{self.templates_directories}/{template_name}") as html:
            content = Template(html.read())

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

        content: str = email_template.substitute(mapping=email_information.model_dump())

        email_message.add_alternative(content, subtype="html")

        _, response_code = await send(
            email_message,
            hostname=self.stmp_host,
            port=self.smtp_port,
            username=self.email,
            password=self.password,
            use_tls=True,
        )

        if response_code != "Message received":
            raise SMTPException("Failed to send email")
