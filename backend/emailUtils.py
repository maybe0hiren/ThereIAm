import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "DFGFGcvbhjgft65e44567uifd"
SALT = "email-verification"
Email = os.getenv('Email')
AppPassword = os.getenv('AppPassword')


serializer = URLSafeTimedSerializer(SECRET_KEY)


def generateVerificationToken(email):
    return serializer.dumps(email, salt=SALT)


def verifyToken(token, max_age=3600):
    try:
        return serializer.loads(token, salt=SALT, max_age=max_age)
    except Exception:
        return None


def sendVerificationEmail(email):
    token = generateVerificationToken(email)

    verifyLink = f"http://localhost:3000/verify-email/{token}"

    msg = MIMEText(
        f"Welcome to ThereIAm!\n\nPlease verify your email:\n{verifyLink}"
    )

    msg["Subject"] = "Verify your ThereIAm account"
    msg["From"] = Email
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(Email, AppPassword)
        server.send_message(msg)
        