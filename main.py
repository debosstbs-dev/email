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

# Create form.html if it doesn't exist
FORM_HTML_PATH = os.path.join(TEMPLATES_DIR, "form.html")
if not os.path.exists(FORM_HTML_PATH):
    print(f"Creating template file at: {FORM_HTML_PATH}")
    form_html_content = """<!DOCTYPE html>
<html>
<head>
    <title>VPN Configuration Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="text"], input[type="email"], input[type="file"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h2>VPN Configuration Form</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label for="sender_email">Your Email:</label>
            <input type="email" id="sender_email" name="sender_email" required>
        </div>

        <div class="form-group">
            <label for="country_name">Country Name:</label>
            <input type="text" id="country_name" name="country_name" required>
        </div>

        <div class="form-group">
            <label for="vpn_name">VPN Name:</label>
            <input type="text" id="vpn_name" name="vpn_name" required>
        </div>

        <div class="form-group">
            <label for="network">Network:</label>
            <input type="text" id="network" name="network" required>
        </div>

        <div class="form-group">
            <label for="file">Upload File:</label>
            <input type="file" id="file" name="file" required>
        </div>

        <button type="submit">Submit</button>
    </form>
</body>
</html>"""
    with open(FORM_HTML_PATH, "w") as f:
        f.write(form_html_content)
    print(f"Template file created successfully")
else:
    print(f"Template file already exists at: {FORM_HTML_PATH}")

print(f"Templates directory contents: {os.listdir(TEMPLATES_DIR)}")

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
