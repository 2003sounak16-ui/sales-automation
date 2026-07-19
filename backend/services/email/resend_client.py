"""
Resend Email Client
===================
Wraps the Resend Python SDK for dispatching outreach emails.
Automatically falls back to mock (console) delivery if RESEND_API_KEY is
missing, invalid, or the API returns an error.

Resend free-tier note
---------------------
Without a verified custom domain, Resend only allows sending FROM
`onboarding@resend.dev` and TO `delivered@resend.dev` (the Resend test
mailbox). Once you add and verify your own domain in the Resend dashboard,
set RESEND_FROM_EMAIL and RESEND_TEST_MODE=false in .env to send to real
recipients.
"""

import os
import logging
import textwrap
from pathlib import Path
from typing import TypedDict, Optional

import resend
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

# Resolve .env from the backend root regardless of cwd.
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH)

logger = logging.getLogger(__name__)

RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")

# When True, all emails are sent TO Resend's test mailbox (delivered@resend.dev)
# which works on free-tier accounts without a verified domain.
# Set RESEND_TEST_MODE=false in .env once you have a verified sender domain.
RESEND_TEST_MODE: bool = os.getenv("RESEND_TEST_MODE", "true").lower() != "false"

# Sender address — use onboarding@resend.dev until you have a verified domain
RESEND_FROM_EMAIL: str = os.getenv(
    "RESEND_FROM_EMAIL", "Sales Automation <onboarding@resend.dev>"
)

is_configured: bool = False

if RESEND_API_KEY and not RESEND_API_KEY.startswith("your-"):
    try:
        resend.api_key = RESEND_API_KEY
        is_configured = True
        mode_label = "TEST MODE" if RESEND_TEST_MODE else "LIVE MODE"
        logger.info("Resend client initialised (%s).", mode_label)
        print(f"Resend Client initialized successfully. [{mode_label}]")
    except Exception as exc:
        logger.error("Failed to initialise Resend client: %s", exc)
        print(f"Failed to initialize Resend client: {exc}")
else:
    logger.warning(
        "RESEND_API_KEY not configured — falling back to mock email client."
    )
    print("RESEND_API_KEY not configured -> using mock email client fallback.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text_to_html(body_text: str) -> str:
    """
    Converts plain-text outreach copy to readable HTML.
    - Double newlines -> paragraph boundaries
    - Single newlines within a paragraph -> <br>
    """
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    return "\n".join(
        f"<p>{para.replace(chr(10), '<br>')}</p>" for para in paragraphs
    )


def _build_html_email(subject: str, body_text: str) -> str:
    """
    Renders the body text inside a polished, responsive HTML email.
    Compatible with major email clients (Gmail, Outlook, Apple Mail).
    """
    body_html = _text_to_html(body_text)

    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <meta http-equiv="X-UA-Compatible" content="IE=edge">
          <title>{subject}</title>
          <!--[if mso]>
          <noscript>
            <xml><o:OfficeDocumentSettings>
              <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings></xml>
          </noscript>
          <![endif]-->
          <style>
            /* Reset */
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
            /* Wrapper */
            .wrapper {{
              width: 100%;
              table-layout: fixed;
              background-color: #f0f2f5;
              padding: 40px 16px;
            }}
            /* Card */
            .card {{
              max-width: 600px;
              margin: 0 auto;
              background: #ffffff;
              border-radius: 16px;
              overflow: hidden;
              box-shadow: 0 4px 32px rgba(0, 0, 0, 0.10);
            }}
            /* Header */
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
            /* Divider accent */
            .header-rule {{
              width: 40px;
              height: 3px;
              background: rgba(255, 255, 255, 0.35);
              border-radius: 2px;
              margin-top: 16px;
            }}
            /* Body */
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
            /* Signature */
            .signature {{
              padding: 0 48px 40px;
              border-top: 1px solid #f3f4f6;
              margin-top: 8px;
              padding-top: 24px;
            }}
            .signature p {{
              font-size: 14px;
              line-height: 1.6;
              color: #6b7280;
            }}
            .signature .name {{
              font-weight: 700;
              color: #111827;
              font-size: 15px;
            }}
            .signature .title {{
              color: #6366f1;
              font-weight: 600;
            }}
            /* Footer */
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
            /* Mobile */
            @media only screen and (max-width: 600px) {{
              .header, .body, .signature, .footer {{
                padding-left: 24px !important;
                padding-right: 24px !important;
              }}
            }}
          </style>
        </head>
        <body>
          <div class="wrapper">
            <div class="card">

              <!-- Header -->
              <div class="header">
                <div class="header-logo">SalesFlow AI</div>
                <div class="header-title">{subject}</div>
                <div class="header-rule"></div>
              </div>

              <!-- Body -->
              <div class="body">
                {body_html}
              </div>

              <!-- Footer -->
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


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class EmailResult(TypedDict):
    status: str    # "success" | "mock_success"
    id: str        # Resend message ID or mock placeholder
    message: str   # Human-readable delivery summary


def send_outreach_email_via_resend(
    to_email: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
) -> EmailResult:
    """
    Send an outreach email via the Resend API.

    In RESEND_TEST_MODE (default), the recipient is overridden to
    Resend's own test mailbox so no domain verification is needed.

    Args:
        to_email:  Intended recipient address.
        subject:   Email subject line.
        body_text: Plain-text body (paragraphs separated by blank lines).

    Returns:
        EmailResult dict with keys: status, id, message.
    """
    # ── Sanitise inputs ───────────────────────────────────────────────────
    intended_recipient = (to_email or "").strip() or "unknown@example.com"
    safe_subject       = (subject   or "Outreach from Sales Automation").strip()
    safe_body          = (body_text or "").strip() or "(No body provided)"

    # ── Resolve actual delivery address ───────────────────────────────────
    # In test mode, Resend only accepts their own test inbox.
    if RESEND_TEST_MODE:
        delivery_address = "delivered@resend.dev"
        logger.info(
            "TEST MODE: redirecting email for %s -> %s",
            intended_recipient, delivery_address
        )
        print(
            f"[TEST MODE] Redirecting email for '{intended_recipient}' "
            f"-> {delivery_address}"
        )
    else:
        delivery_address = intended_recipient

    # ── Live dispatch ─────────────────────────────────────────────────────
    if is_configured:
        try:
            html_content = _build_html_email(safe_subject, safe_body)

            # "from" is a Python reserved word; pass it inside a plain dict.
            params: resend.Emails.SendParams = {
                "from": RESEND_FROM_EMAIL,
                "to": [delivery_address],
                "subject": safe_subject,
                "html": html_content,
            }  # type: ignore[assignment]

            response: resend.Emails.SendResponse = resend.Emails.send(params)

            # SendResponse is a TypedDict — access via key, not attribute.
            email_id: str = response["id"]

            logger.info(
                "Email dispatched via Resend -> %s (id=%s)",
                delivery_address, email_id,
            )
            print(
                f"[OK] Email sent via Resend to {delivery_address} "
                f"[id={email_id}]"
            )

            return EmailResult(
                status="success",
                id=email_id,
                message=(
                    f"Email dispatched via Resend to {delivery_address} "
                    f"(intended: {intended_recipient})"
                ),
            )

        except Exception as exc:
            logger.error(
                "Resend dispatch failed for %s: %s -- falling back to mock.",
                delivery_address, exc,
            )
            print(f"[ERROR] Resend error for {delivery_address}: {exc}  -> mock fallback")

    # ── Mock fallback ─────────────────────────────────────────────────────
    mock_id = "mock-00000000-0000-0000-0000-000000000000"
    print(f"[MOCK] Email dispatched to {intended_recipient}")
    print(f"  Subject : {safe_subject}")
    print(f"  Body    :\n{safe_body}")

    return EmailResult(
        status="mock_success",
        id=mock_id,
        message=f"[Mock] Email successfully dispatched to {intended_recipient}",
    )
