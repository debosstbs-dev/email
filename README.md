# VPN Configuration Form

A FastAPI application that provides a form for submitting VPN configurations with file attachments. The form data is sent via email to the administrator.

## Features

- Web form for VPN configuration submission
- File upload capability
- Email notification system
- Docker support for easy deployment

## Prerequisites

- Docker installed on your system
- SMTP server credentials (already configured in the application)

## Building and Running with Docker

1. Build the Docker image:
```bash
docker build -t vpn-config-form .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 vpn-config-form
```

The application will be available at `http://localhost:8000`

## Environment Variables

The following environment variables can be configured:
- SMTP_SERVER: SMTP server address (default: smtp.hostinger.com)
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USERNAME: SMTP username
- SMTP_PASSWORD: SMTP password
- ADMIN_EMAIL: Administrator email address

## Development

If you want to run the application without Docker:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
``` 