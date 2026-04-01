import aiosmtplib
from email.message import EmailMessage
import logging
import os 
from dotenv import load_dotenv
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


# ✅ Singleton instance (easy import anywhere)
email_service = EmailService()