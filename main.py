import imaplib 
import os
import email
import re
import requests
from dotenv import load_dotenv

load_dotenv()

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
imap_server = os.getenv("IMAP_SERVER")

def connect_to_email():
    """Connects to the email server via IMAP."""
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, email_password)
        mail.select('inbox')  # Access inbox
        return mail
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None
    
def fetch_emails(mail):
    """Fetches emails from the inbox."""
    try:
        # Search all emails
        _, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        return email_ids
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []
    
def extract_unsubscribe_link(email_message):
    """Extracts the unsubscribe link from an email message."""
    unsubscribe_link = None
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode()
                # Look for "unsubscribe" links
                match = re.search(r'href=["\'](https?://.*?unsubscribe.*?)["\']', html_content, re.IGNORECASE)
                if match:
                    unsubscribe_link = match.group(1)
                    break
    return unsubscribe_link

def unsubscribe_from_newsletter(link):
    """Unsubscribes from a newsletter by following the unsubscribe link."""
    try:
        response = requests.get(link, allow_redirects=True)
        if response.status_code == 200:
            print(f"Unsubscribed successfully from link: {link}!")
        else:
            print(f"Failed to access unsubscribe link: {link}")
    except Exception as e:
        print(f"Error unsubscribing: {e}")
        
def process_emails(mail):
    """Processes emails by extracting unsubscribe links and unsubscribing from newsletters."""
    email_ids = fetch_emails(mail)
    for email_id in email_ids:
        try:
            _, data = mail.fetch(email_id, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract unsubscribe link
            link = extract_unsubscribe_link(email_message)
            if link:
                print(f"Unsubscribe link found: {link}")
                unsubscribe_from_newsletter(link)
            else:
                print(f"No unsubscribe link found in email {email_id}")
        
        except Exception as e:
            print(f"Error processing email ID {email_id}: {e}")
            
def main():
    mail = connect_to_email()
    if mail:
        process_emails(mail)
        mail.logout()
        
if __name__=="__main__":
    main()

