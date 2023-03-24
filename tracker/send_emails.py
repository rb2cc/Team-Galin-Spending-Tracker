
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from dotenv import load_dotenv

PORT = 587
EMAIL_SERVER = 'smtp.gmail.com'

# Load the environment variables

current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

# Read environment variables

sender_email = "teamgalin.moneysaver@gmail.com"
password_email = "boqk cfkx yybp uhxt"


class Emailer:

    def send_email(subject, receiver_email, name):
    # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            I hope you are doing well,

            Please use our web application again.

            Thanks.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> I hope you are doing well,</p>
                <p> <strong> Please use our web application again. </strong> </p>
                <p> Thanks. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())



    def send_register_email(subject, receiver_email, name):
    # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            Thank you for registering your account.

            Please visit out website to begin using your account.

            We are here to support you.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> Thank you for registering your account.</p>
                <p> <strong> Please visit out website to begin using your account. </strong> </p>
                <p> We are here to support you. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())


    # Method to send email for registration.

    def send_register_email(subject, receiver_email, name):
    # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            Thank you for registering your account.

            Please visit out website to begin using your account.

            We are here to support you.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> Thank you for registering your account.</p>
                <p> <strong> Please visit out website to begin using your account. </strong> </p>
                <p> We are here to support you. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())

    # Method to send email for reminder for various functions.

    def send_reminder_email(subject, receiver_email, name, reminderType):
    # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            Thank you for registering your account.

            Please visit out website to begin using your account.

            We are here to support you.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> Thank you for registering your account.</p>
                <p> <strong> Please visit out website to begin using your account. </strong> </p>
                <p> We are here to support you. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            


    def send_spending_limit_notification(subject, receiver_email, name):
     # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            You are nearing the spending limit of one of your categories.

            Please visit out website to check on your spending.

            We are here to support you.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> You are nearing the spending limit of one of your categories. </p>
                <p> <strong> Please visit out website to check on your spending. </strong> </p>
                <p> We are here to support you. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())


def send_spending_limit_notification(subject, receiver_email, name):
     # Create the base text message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Team Galin Money Saver.", f"{sender_email}"))
        msg["To"] = receiver_email
        msg["BCC"] = sender_email

        msg.set_content(
            f"""\
            Hi {name},

            You are nearing the spending limit of one of your categories.

            Please visit out website to check on your spending.

            We are here to support you.

            Kind regards,

            Team Galin Money Saver.
            """
    )

    # Add html version. This converts the messagee into a multipart/alternative
    # container, with the original message as the first part and th new html
    # message as the second part.

        msg.add_alternative(
            f"""\
                <html>
                <body>
                <p> Hi {name}, </p>
                <p> You are nearing the spending limit of one of your categories. </p>
                <p> <strong> Please visit out website to check on your spending. </strong> </p>
                <p> We are here to support you. </p>
                <p> Kind regards, </p>
                <p> Team Galin Money Saver. </p>
                </body>
                </html>
                """,

                subtype = "html",
        )


        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, msg.as_string())



if __name__ == "__main__":
        Emailer.send_email(
        subject="test",
        name="test testing",
        receiver_email="ricky.brown@richmond.edu"
        )

