import os
import base64
import pickle
from email import message_from_bytes, policy
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for reading Gmail messages
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def extract_raw_email(email_bytes):
    """Reconstructs a raw email with human-readable plain text body and attachments."""
    msg = message_from_bytes(email_bytes, policy=policy.default)

    # Extract headers
    email_headers = {
        "Message-ID": msg["Message-ID"],
        "Date": msg["Date"],
        "From": msg["From"],
        "To": msg["To"],
        "Subject": msg["Subject"],
        "Mime-Version": "1.0"
    }

    # Start building the raw email
    raw_email = []
    
    # Add headers
    for key, value in email_headers.items():
        if value:  # Only add headers that exist
            raw_email.append(f"{key}: {value}")

    # Define boundary
    boundary = "boundary123"
    raw_email.append(f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\n")

    # Extract plain text body
    plain_text_body = None
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                # Extract plain text body (fully decoded, no base64)
                charset = part.get_content_charset() or "utf-8"
                try:
                    plain_text_body = part.get_payload(decode=True).decode(charset, errors="ignore").strip()
                except Exception:
                    plain_text_body = "Error decoding text content."

            elif content_disposition and "attachment" in content_disposition:
                # Extract attachment
                filename = part.get_filename()
                payload = part.get_payload(decode=True)

                if filename and payload:
                    attachments.append((filename, payload))

    else:
        # Handle single-part email (non-multipart)
        charset = msg.get_content_charset() or "utf-8"
        if msg.get_content_type() == "text/plain":
            plain_text_body = msg.get_payload(decode=True).decode(charset, errors="ignore").strip()

    # Ensure the body is directly added as plain text
    if plain_text_body:
        raw_email.append(f"--{boundary}")
        raw_email.append("Content-Type: text/plain; charset=\"UTF-8\"")
        raw_email.append("Content-Transfer-Encoding: 7bit\n")
        raw_email.append(plain_text_body + "\n")  # Ensuring plain text is inserted directly

    # Attachments (if any)
    for filename, payload in attachments:
        encoded_attachment = base64.b64encode(payload).decode("utf-8")
        raw_email.append(f"--{boundary}")
        raw_email.append(f"Content-Type: application/octet-stream")
        raw_email.append(f"Content-Disposition: attachment; filename=\"{filename}\"")
        raw_email.append("Content-Transfer-Encoding: base64\n")
        raw_email.append(encoded_attachment + "\n")

    # End boundary
    raw_email.append(f"--{boundary}--\n")

    # Convert list to full email string
    return "\n".join(raw_email)

def fetch_and_format_emails(label='INBOX'):
    """Fetch and reconstruct the latest Gmail inbox messages in proper raw format."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', labelIds=[label], maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new messages found.")
        return
    raw_emails = []
    for msg in messages:
        msg_id = msg['id']
        msg_data = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()

        raw_email_b64 = msg_data.get('raw')
        if raw_email_b64:
            # Decode Base64 and reconstruct raw email
            raw_email_bytes = base64.urlsafe_b64decode(raw_email_b64)
            formatted_email = extract_raw_email(raw_email_bytes)

            # print("\n==== RECONSTRUCTED RAW EMAIL ====\n")
            raw_emails.append(formatted_email)
            # print(formatted_email)
            # print("\n=================================\n")
        else:
            print("Warning: No raw email content available for message ID:", msg_id)

        # print("=" * 100)
    return raw_emails
        

if __name__ == '__main__':
    fetch_and_format_emails()
