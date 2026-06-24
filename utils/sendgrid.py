import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(subject, to_emails, html_content, from_email='web@geneva.edu'):
    try:
        message = Mail(
            from_email='web@geneva.edu',
            to_emails='hmschult1@geneva.edu',
            subject='New Alumni Update Form Submission',
            html_content=html_content
        )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print("Email sent:", response.status_code)
    except Exception as e:
        print("Email error:", str(e))