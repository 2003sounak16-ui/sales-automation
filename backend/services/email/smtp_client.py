import os
import smtplib
import logging
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TypedDict, Optional
from dotenv import load_dotenv
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH)

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "2003sounak16@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailResult(TypedDict):
    status: str
    id: str
    message: str

def _text_to_html(body_text: str) -> str:
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    return "\n".join(
        f"<p>{para.replace(chr(10), '<br>')}</p>" for para in paragraphs
    )

def _build_html_email(subject: str, body_text: str) -> str:
    body_html = _text_to_html(body_text)

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <meta http-equiv="X-UA-Compatible" content="IE=edge">
          <title>{subject}</title>
          <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body, html {{
              width: 100% !important;
              height: 100%;
              margin: 0;
              padding: 0;
              background-color: #f0f2f5;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                           Roboto, 'Helvetica Neue', Arial, sans-serif;
              -webkit-font-smoothing: antialiased;
              -moz-osx-font-smoothing: grayscale;
            }}
            .wrapper {{
              width: 100%;
              table-layout: fixed;
              background-color: #f0f2f5;
              padding: 40px 16px;
            }}
            .card {{
              max-width: 600px;
              margin: 0 auto;
              background: #ffffff;
              border-radius: 16px;
              overflow: hidden;
              box-shadow: 0 4px 32px rgba(0, 0, 0, 0.10);
            }}
            .header {{
              background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 60%, #7c3aed 100%);
              padding: 36px 48px 32px;
            }}
            .header-logo {{
              font-size: 13px;
              font-weight: 700;
              letter-spacing: 0.12em;
              text-transform: uppercase;
              color: rgba(255, 255, 255, 0.55);
              margin-bottom: 10px;
            }}
            .header-title {{
              font-size: 22px;
              font-weight: 700;
              color: #ffffff;
              line-height: 1.3;
              letter-spacing: -0.02em;
            }}
            .header-rule {{
              width: 40px;
              height: 3px;
              background: rgba(255, 255, 255, 0.35);
              border-radius: 2px;
              margin-top: 16px;
            }}
            .body {{
              padding: 40px 48px 32px;
            }}
            .body p {{
              font-size: 15px;
              line-height: 1.8;
              color: #374151;
              margin-bottom: 18px;
            }}
            .body p:last-child {{
              margin-bottom: 0;
            }}
            .footer {{
              background: #f9fafb;
              border-top: 1px solid #e5e7eb;
              padding: 20px 48px;
              text-align: center;
            }}
            .footer p {{
              font-size: 11px;
              color: #9ca3af;
              line-height: 1.6;
            }}
            .footer a {{
              color: #6366f1;
              text-decoration: none;
            }}
            @media only screen and (max-width: 600px) {{
              .header, .body, .footer {{
                padding-left: 24px !important;
                padding-right: 24px !important;
              }}
            }}
          </style>
        </head>
        <body>
          <div class="wrapper">
            <div class="card">
              <div class="header">
                <div class="header-logo">SalesFlow AI</div>
                <div class="header-title">{subject}</div>
                <div class="header-rule"></div>
              </div>
              <div class="body">
                {body_html}
              </div>
              <div class="footer">
                <p>
                  You are receiving this email as part of a targeted outreach campaign.<br>
                  &copy; 2025 SalesFlow AI &middot;
                  <a href="#">Unsubscribe</a>
                </p>
              </div>
            </div>
          </div>
        </body>
        </html>
    """)

def send_outreach_email_via_smtp(
    to_email: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
) -> EmailResult:
    """
    Send an outreach email via standard SMTP (Gmail).
    """
    intended_recipient = (to_email or "").strip() or "unknown@example.com"
    safe_subject = (subject or "Outreach from Sales Automation").strip()
    safe_body = (body_text or "").strip() or "(No body provided)"

    if not SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD not configured - falling back to mock email.")
        print("[MOCK] SMTP_PASSWORD is not set.")
        print(f"  To      : {intended_recipient}")
        print(f"  Subject : {safe_subject}")
        print(f"  Body    :\n{safe_body}")
        return EmailResult(
            status="mock_success",
            id="mock-smtp-0000",
            message=f"[Mock] Email successfully dispatched to {intended_recipient} from {SMTP_EMAIL}",
        )

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = safe_subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = intended_recipient

        html_content = _build_html_email(safe_subject, safe_body)
        
        part1 = MIMEText(safe_body, 'plain')
        part2 = MIMEText(html_content, 'html')

        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, intended_recipient, msg.as_string())
        server.quit()

        print(f"[OK] Email sent via SMTP to {intended_recipient}")
        return EmailResult(
            status="success",
            id="smtp-delivered",
            message=f"Email dispatched via SMTP to {intended_recipient}",
        )
    except Exception as exc:
        logger.error("SMTP dispatch failed for %s: %s", intended_recipient, exc)
        print(f"[ERROR] SMTP error for {intended_recipient}: {exc}")
        
        return EmailResult(
            status="failed",
            id="",
            message=f"Failed to send via SMTP: {exc}"
        )
