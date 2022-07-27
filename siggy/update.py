from genericpath import exists
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from siggy.templates import load_template

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.settings.basic"]


def get_credentials() -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            InstalledAppFlow()
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def build_gmail_service(credentials: Credentials):
    return build("gmail", "v1", credentials=credentials)


def get_primary_send_as_email(service) -> str:

    # pylint: disable=E1101
    aliases = service.users().settings().sendAs().list(userId="me").execute()
    for alias in aliases.get("sendAs"):
        if alias.get("isPrimary"):
            primary_alias = alias
            break

    return primary_alias.get("sendAsEmail")


def update_signature(service, email: str, new_signature: str) -> None:
    send_as_configuration = {"signature": new_signature}

    result = (
        service.users()
        .settings()
        .sendAs()
        .patch(
            userId="me",
            sendAsEmail=email,
            body=send_as_configuration,
        )
        .execute()
    )
    print(result)


def execute(name: str, role: str, phone: str):
    creds = get_credentials()
    service = build_gmail_service(creds)
    send_as_email = get_primary_send_as_email(service)

    signature = load_template(
        name,
        role,
        send_as_email,
        phone,
    )

    update_signature(service, send_as_email, signature)
