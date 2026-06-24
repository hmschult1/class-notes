"""Simple SendGrid wrapper used to notify site admins on new submissions.

This module is intentionally small: it constructs a `Mail` object and
uses the `SENDGRID_API_KEY` environment variable. In development the
function will print errors instead of raising so failures don't break
the submission flow.
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(subject, to_emails, html_content, from_email='web@geneva.edu'):
    """Send a notification email using SendGrid.

    `SENDGRID_API_KEY` must be set in the environment for delivery.
    The function logs status and swallows exceptions to avoid failing
    end-user submissions when email delivery has problems.
    """
    try:
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print("Email sent:", response.status_code)
    except Exception as e:
        # Log the error; do not raise so the user flow continues.
        print("Email error:", str(e))