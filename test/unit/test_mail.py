# client = EmailClient()

# usuario = UserBaseEmail(
#    name="Ezequiel",
#    lastname="Gutierrez",
#    frontend_url=HttpUrl("http://localhost:8000"),
#    year=2025,
# )


# client.send_email(
#    subject="Nuevo Usuario",
#    email="Eze412002.eg@gmail.com",
#    email_information=usuario,
#    template_name=TemplateHTML.VERIFICATION,
# )


# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

# creds = flow.run_local_server(port=0)

# with open("token.json", "w") as token:
#    token.write(creds.to_json())
from app.services import SecurityService

password = SecurityService().hash_password("elonmusk1$")

print(password)
