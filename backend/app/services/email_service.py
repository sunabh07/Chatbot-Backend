import aiosmtplib
from email.message import EmailMessage
import logging
import os 
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from fastapi import HTTPException,status
load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
       
        self.EMAIL_HOST = os.getenv("EMAIL_HOST")
        self.EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
        self.EMAIL_USER = os.getenv("EMAIL_USER")
        self.EMAIL_PASS = os.getenv("EMAIL_PASS")

    async def send_mail(self, to_email: str, subject: str, body: str) -> str:
        """
        Send an email using Gmail SMTP
        """

        try:
            message = EmailMessage()
            message["From"] = self.EMAIL_USER
            message["To"] = to_email
            message["Subject"] = subject
            message.set_content(body)

            await aiosmtplib.send(
                message,
                hostname=self.EMAIL_HOST,
                port=self.EMAIL_PORT,
                start_tls=True,
                username=self.EMAIL_USER,
                password=self.EMAIL_PASS,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return "Email sent successfully"

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")
    
    def get_mail(self,limit=100):
        
        try:

            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.EMAIL_USER, self.EMAIL_PASS)

            mail.select("inbox")

            status, messages = mail.search(None, "ALL")

            mail_ids = messages[0].split()

            emails=[]
            for i in mail_ids[-limit:]:
                status, msg_data = mail.fetch(i, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject, _ = decode_header(msg["subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                emails.append({
                    "from": msg.get("from"),
                    "subject": subject
                })

            return emails
        except Exception as e:
            logger.error("Error occured during get mail function")
            raise Exception(
                detail=f"Error occured during fetching emails,{e}"
            )

# ✅ Singleton instance (easy import anywhere)
email_service = EmailService()