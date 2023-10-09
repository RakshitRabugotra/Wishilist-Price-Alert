import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

# Load the env Variables
load_dotenv()

class Mail:
    def __init__(self, email_address: str, email_passwd: str):
        self.EMAIL_ADDRESS = email_address
        self.EMAIL_PASSWD = email_passwd

    def send_mail(self, subject: str, to: str, content: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.EMAIL_ADDRESS
        msg["To"] = to
        msg.set_content(content)

        # Send the message
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWD)
            smtp.send_message(msg)
    

if __name__ == '__main__':
    ea = os.environ["EMAIL_ADDRESS"]
    ep = os.environ["EMAIL_PASSWD"]

    receiver = input("Enter receiver's address: ")
    content = input("The content for the mail: ")
    
    mail_object = Mail(ea, ep)
    mail_object.send_mail("Testing", receiver, content)
