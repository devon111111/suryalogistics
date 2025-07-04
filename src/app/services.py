from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import os
from dotenv import load_dotenv
from app.models import ContactForm

load_dotenv()

# --- CONFIGURATION ---
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = 587
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
IMAGE_DIR = "static/image"

valid_uuids = set()

def generate_uuid_header():
    session_uuid = str(uuid.uuid4())
    valid_uuids.add(session_uuid)
    return {"X-Session-UUID": session_uuid}

def send_email_background(form: ContactForm):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = "🚚 New Delivery Request from an Agent"
        today = date.today()
        if form.shifting_date == today:
            date_label = "Today"
        elif form.shifting_date == today + timedelta(days=1):
            date_label = "Tomorrow"
        else:
            date_label = "📅 Upcoming"

        formatted_date = form.shifting_date.strftime('%d-%m-%Y')

        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #333333;
                }}
                p {{
                    line-height: 1.6;
                    color: #555555;
                }}
                .label {{
                    font-weight: bold;
                    color: #111;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚛 New Delivery Submission</h2>
                <h3>You have received a new delivery request from an agent. Details are below:</h3>
                <h4><span class="label">📞 Phone:</span> {form.phone}</h4>
                <h4><span class="label">📍 Pickup Location:</span> {form.pickup_location}</h4>
                <h4><span class="label">📦 Drop-off Location:</span> {form.drop_location or 'Not provided'}</h4>
                <h4><span class="label">📅 Shifting Date:</span> {formatted_date} <strong>({date_label})</strong></h4>
                <br>
                <h2>🚀 Please follow up with the agent as soon as possible to confirm the logistics.</h2>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Failed to send email:", e)