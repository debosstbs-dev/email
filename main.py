from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import uvicorn

# Get the absolute path of the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure directories exist
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI()

# Mount templates with absolute path
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Only mount static files if directory exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    try:
        return templates.TemplateResponse("form.html", {"request": request})
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        print(f"Templates directory: {TEMPLATES_DIR}")
        print(f"Directory contents: {os.listdir(TEMPLATES_DIR)}")
        raise

@app.post("/submit")
async def submit_form(
    sender_email: str = Form(...),
    country_name: str = Form(...),
    vpn_name: str = Form(...),
    network: str = Form(...),
    file: UploadFile = File(...)
):
    # Save the uploaded file temporarily
    file_location = os.path.join(UPLOADS_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    # Create email
    msg = MIMEMultipart()
    msg['From'] = "admin@kofnet.co.za"  # Use authenticated email as sender
    msg['Reply-To'] = sender_email      # Add reply-to header with user's email
    msg['To'] = "admin@kofnet.co.za"
    msg['Subject'] = f"New VPN Configuration Submission from {sender_email}"

    # Email body
    body = f"""
    New VPN configuration submission:
    
    Submitted by: {sender_email}
    Country Name: {country_name}
    VPN Name: {vpn_name}
    Network: {network}
    
    To reply to this submission, please email: {sender_email}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    with open(file_location, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="txt")
        attachment.add_header('Content-Disposition', 'attachment', filename=file.filename)
        msg.attach(attachment)

    # Send email
    try:
        # Updated SMTP settings
        smtp_server = "smtp.hostinger.com"
        smtp_port = 587
        smtp_username = "admin@kofnet.co.za"
        smtp_password = "Mm@629857"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        # Clean up the uploaded file
        os.remove(file_location)

        return {"message": "Form submitted successfully"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 
