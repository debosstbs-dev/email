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

app = FastAPI()

# Mount templates
templates = Jinja2Templates(directory="templates")

# Only mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit")
async def submit_form(
    sender_email: str = Form(...),
    country_name: str = Form(...),
    vpn_name: str = Form(...),
    network: str = Form(...),
    file: UploadFile = File(...)
):
    # Save the uploaded file temporarily
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
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
