"""
app/services/email_service.py — Email dispatch service supporting SMTP and Resend API.
"""
import asyncio
import html
import json
import logging
import smtplib
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from app.schemas.email import EmailSendRequest, EmailSendResponse

logger = logging.getLogger("hiremate.email")


def _build_html_email(request: EmailSendRequest) -> str:
    """Build a modern, branded HTML email template."""
    recipient_name = request.to_name or "Candidate"
    
    # Escape body content for safe HTML rendering and preserve linebreaks
    escaped_body = html.escape(request.body)
    paragraphs = [f"<p style='margin: 0 0 16px 0; line-height: 1.6; color: #334155; font-size: 15px;'>{p.replace('\n', '<br/>')}</p>" 
                  for p in escaped_body.split("\n\n") if p.strip()]
    body_html = "".join(paragraphs)

    interview_box = ""
    if request.is_interview or request.interview_date or request.meeting_link:
        meeting_button = ""
        if request.meeting_link:
            meeting_button = f"""
            <div style="margin-top: 20px; text-align: center;">
                <a href="{html.escape(request.meeting_link)}" target="_blank"
                   style="display: inline-block; background: #2563eb; color: #ffffff; padding: 12px 28px; font-weight: 600; font-size: 14px; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);">
                   👉 Join Video Interview
                </a>
            </div>
            """
        interview_box = f"""
        <div style="margin: 24px 0; padding: 20px; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #166534; font-size: 16px; font-weight: 700;">📅 Scheduled Interview Details</h4>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #1e293b;">
                {f'<tr><td style="padding: 6px 0; font-weight: 600; color: #475569; width: 110px;">Date:</td><td style="padding: 6px 0; font-weight: 700; color: #0f172a;">{html.escape(request.interview_date)}</td></tr>' if request.interview_date else ''}
                {f'<tr><td style="padding: 6px 0; font-weight: 600; color: #475569;">Time:</td><td style="padding: 6px 0; font-weight: 700; color: #0f172a;">{html.escape(request.interview_time)}</td></tr>' if request.interview_time else ''}
                {f'<tr><td style="padding: 6px 0; font-weight: 600; color: #475569;">Meeting Link:</td><td style="padding: 6px 0;"><a href="{html.escape(request.meeting_link)}" style="color: #2563eb; text-decoration: underline; word-break: break-all;">{html.escape(request.meeting_link)}</a></td></tr>' if request.meeting_link else ''}
            </table>
            {meeting_button}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(request.subject)}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 32px 16px;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01); border: 1px solid #e2e8f0;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 28px 36px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 3px solid #3b82f6;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td>
                                            <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">
                                                FAZESOFT <span style="color: #60a5fa; font-weight: 400;">EMS</span>
                                            </h1>
                                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Talent Acquisition & HR Operations</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 36px 36px 28px 36px;">
                                <div style="margin-bottom: 24px;">
                                    <h2 style="margin: 0 0 8px 0; color: #0f172a; font-size: 18px; font-weight: 700;">{html.escape(request.subject)}</h2>
                                    <p style="margin: 0; color: #64748b; font-size: 13px;">Recipient: <strong style="color: #334155;">{html.escape(recipient_name)}</strong> &lt;{html.escape(request.to_email)}&gt;</p>
                                </div>
                                <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 0 0 24px 0;" />

                                <!-- Main Body -->
                                <div style="color: #334155;">
                                    {body_html}
                                </div>

                                <!-- Optional Interview Callout -->
                                {interview_box}
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 36px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0 0 6px 0; font-size: 13px; font-weight: 600; color: #475569;">
                                    {html.escape(settings.SMTP_FROM_NAME or "FazeSoft Recruitment Team")}
                                </p>
                                <p style="margin: 0 0 12px 0; font-size: 12px; color: #94a3b8;">
                                    FazeSoft Enterprise Management System &middot; Automated Notification
                                </p>
                                <p style="margin: 0; font-size: 11px; color: #cbd5e1; line-height: 1.4;">
                                    This email was sent to {html.escape(request.to_email)}. If you received this in error, please disregard.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """.strip()


def _send_smtp_sync(
    host: str,
    port: int,
    user: Optional[str],
    password: Optional[str],
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str,
    use_tls: bool = True,
    use_ssl: bool = False,
) -> None:
    """Synchronous SMTP sending logic run inside asyncio.to_thread."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    msg["To"] = to_email

    part_text = MIMEText(body_text, "plain", "utf-8")
    part_html = MIMEText(body_html, "html", "utf-8")
    msg.attach(part_text)
    msg.attach(part_html)

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=15) as server:
            if user and password:
                server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())
    else:
        with smtplib.SMTP(host, port, timeout=15) as server:
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())


def _send_resend_api_sync(api_key: str, from_email: str, from_name: str, to_email: str, subject: str, body_html: str) -> dict:
    """Send via Resend HTTP REST API."""
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "FazeSoft-EMS/1.0",
    }
    payload = {
        "from": f"{from_name} <{from_email}>" if from_name else from_email,
        "to": [to_email],
        "subject": subject,
        "html": body_html,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_data = resp.read().decode("utf-8")
            return json.loads(resp_data) if resp_data else {"id": "accepted"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("message") or error_json.get("error") or error_body
        except Exception:
            error_msg = error_body
        raise RuntimeError(f"Resend API returned {e.code}: {error_msg}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Resend network connection error: {e.reason}") from e


class EmailService:
    @staticmethod
    async def send_candidate_email(request: EmailSendRequest) -> EmailSendResponse:
        """
        Send an email to a candidate using configured SMTP or Resend API.
        If no credentials are configured, returns a descriptive response so
        the frontend can activate Gmail / Outlook / mailto fallbacks seamlessly.
        """
        html_content = _build_html_email(request)
        plain_text = request.body
        if request.is_interview and (request.interview_date or request.meeting_link):
            plain_text += f"\n\n--- Interview Details ---\nDate: {request.interview_date}\nTime: {request.interview_time}\nMeeting Link: {request.meeting_link}"

        from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER or "recruitment@fazesoft.com"
        from_name = settings.SMTP_FROM_NAME or "FazeMate Recruitment Team"

        # 1. Try Resend API if key is present
        if settings.RESEND_API_KEY:
            resend_from_email = settings.RESEND_FROM_EMAIL or "onboarding@resend.dev"
            try:
                result = await asyncio.to_thread(
                    _send_resend_api_sync,
                    settings.RESEND_API_KEY,
                    resend_from_email,
                    from_name,
                    request.to_email,
                    request.subject,
                    html_content,
                )
                email_id = result.get("id", "accepted") if isinstance(result, dict) else "accepted"
                logger.info("Email delivered via Resend API to %s (ID: %s)", request.to_email, email_id)
                return EmailSendResponse(
                    success=True,
                    status="sent",
                    message=f"Email successfully delivered to {request.to_email} via Resend (ID: {email_id})",
                    provider="resend",
                    recipient=request.to_email,
                )
            except Exception as e:
                logger.error("Resend API send failed: %s", e)
                # If SMTP is not explicitly configured, return the exact Resend error
                if not settings.SMTP_HOST:
                    return EmailSendResponse(
                        success=False,
                        status="resend_error",
                        message=str(e),
                        provider="resend",
                        recipient=request.to_email,
                    )

        # 2. Try SMTP if host is present
        if settings.SMTP_HOST:
            try:
                await asyncio.to_thread(
                    _send_smtp_sync,
                    settings.SMTP_HOST,
                    settings.SMTP_PORT,
                    settings.SMTP_USER,
                    settings.SMTP_PASSWORD,
                    from_email,
                    from_name,
                    request.to_email,
                    request.subject,
                    plain_text,
                    html_content,
                    settings.SMTP_TLS,
                    settings.SMTP_SSL,
                )
                logger.info("Email delivered via SMTP to %s", request.to_email)
                return EmailSendResponse(
                    success=True,
                    status="sent",
                    message=f"Email successfully delivered to {request.to_email}",
                    provider="smtp",
                    recipient=request.to_email,
                )
            except Exception as e:
                logger.error("SMTP send failed: %s", e)
                return EmailSendResponse(
                    success=False,
                    status="smtp_error",
                    message=f"Failed to send email via SMTP server: {str(e)}",
                    recipient=request.to_email,
                )

        # 3. Neither SMTP nor Resend is configured
        logger.warning("Email request received for %s, but no SMTP or Resend credentials are configured.", request.to_email)
        return EmailSendResponse(
            success=False,
            status="smtp_not_configured",
            message="No SMTP credentials configured on backend. Use Gmail, Outlook, or client fallback.",
            recipient=request.to_email,
        )

    @staticmethod
    async def send_task_assignment_email(
        recipient_email: str,
        recipient_name: str,
        task_title: str,
        task_description: str,
        project_name: str,
        priority: str,
        deadline: str,
        assigned_by_name: str,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> bool:
        """
        Send an automated email notification when a task is assigned to a user.
        Dispatches via Resend API or SMTP server with graceful fallback and logging.
        """
        try:
            frontend_base = (settings.FRONTEND_URL or "http://localhost:3000").rstrip("/")
            task_url = f"{frontend_base}/ems/dashboard/projects/{project_id}" if project_id else f"{frontend_base}/ems/dashboard/tasks"

            html_content = _build_task_assignment_html_email(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                task_title=task_title,
                task_description=task_description,
                project_name=project_name,
                priority=priority,
                deadline=deadline,
                assigned_by_name=assigned_by_name,
                task_url=task_url,
            )

            plain_text = (
                f"Hello {recipient_name},\n\n"
                f"You have been assigned a new task in project '{project_name}'.\n\n"
                f"Task Title: {task_title}\n"
                f"Project: {project_name}\n"
                f"Priority: {priority}\n"
                f"Deadline: {deadline}\n"
                f"Assigned By: {assigned_by_name}\n\n"
                f"Description:\n{task_description}\n\n"
                f"View Task: {task_url}\n\n"
                f"— FazeSoft EMS Automated Notification"
            )

            subject = f"[FazeSoft EMS] New Task Assigned: {task_title}"
            from_name = "FazeSoft EMS"

            # 1. Try Resend API if key is present
            if settings.RESEND_API_KEY:
                resend_from_email = settings.RESEND_FROM_EMAIL or "onboarding@resend.dev"
                try:
                    res = await asyncio.to_thread(
                        _send_resend_api_sync,
                        settings.RESEND_API_KEY,
                        resend_from_email,
                        from_name,
                        recipient_email,
                        subject,
                        html_content,
                    )
                    email_id = res.get("id", "accepted") if isinstance(res, dict) else "accepted"
                    logger.info("Task assignment email delivered via Resend to %s (Task: '%s', ID: %s)", recipient_email, task_title, email_id)
                    return True
                except Exception as e:
                    logger.warning("Resend API delivery to %s failed: %s. Attempting SMTP if configured...", recipient_email, e)

            # 2. Try SMTP if host is present
            if settings.SMTP_HOST:
                try:
                    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER or "no-reply@fazesoft.com"
                    await asyncio.to_thread(
                        _send_smtp_sync,
                        settings.SMTP_HOST,
                        settings.SMTP_PORT,
                        settings.SMTP_USER,
                        settings.SMTP_PASSWORD,
                        from_email,
                        from_name,
                        recipient_email,
                        subject,
                        plain_text,
                        html_content,
                        settings.SMTP_TLS,
                        settings.SMTP_SSL,
                    )
                    logger.info("Task assignment email delivered via SMTP to %s (Task: '%s')", recipient_email, task_title)
                    return True
                except Exception as e:
                    logger.error("SMTP delivery to %s failed: %s", recipient_email, e)
                    return False

            if not settings.RESEND_API_KEY and not settings.SMTP_HOST:
                logger.info("No email credentials configured; task notification to %s skipped.", recipient_email)
            return False

        except Exception as err:
            logger.error("Unexpected error in send_task_assignment_email to %s: %s", recipient_email, err, exc_info=True)
            return False


def _build_task_assignment_html_email(
    recipient_email: str,
    recipient_name: str,
    task_title: str,
    task_description: str,
    project_name: str,
    priority: str,
    deadline: str,
    assigned_by_name: str,
    task_url: str,
) -> str:
    """Build a modern, branded HTML email template for task assignment notifications."""
    safe_recipient = html.escape(recipient_name or "Team Member")
    safe_title = html.escape(task_title)
    safe_project = html.escape(project_name)
    safe_assigner = html.escape(assigned_by_name or "Project Lead")
    safe_deadline = html.escape(deadline)

    # Priority badge styling
    p_upper = (priority or "Medium").strip().capitalize()
    if p_upper == "High":
        priority_bg = "#fee2e2"
        priority_color = "#dc2626"
        priority_border = "#fca5a5"
    elif p_upper == "Low":
        priority_bg = "#dcfce7"
        priority_color = "#16a34a"
        priority_border = "#86efac"
    else:  # Medium
        priority_bg = "#fef3c7"
        priority_color = "#d97706"
        priority_border = "#fcd34d"

    # Format description paragraphs safely
    escaped_desc = html.escape(task_description or "No additional description provided.")
    paragraphs = [
        f"<p style='margin: 0 0 12px 0; line-height: 1.6; color: #334155; font-size: 14px;'>{p.replace(chr(10), '<br/>')}</p>"
        for p in escaped_desc.split("\n\n") if p.strip()
    ]
    description_html = "".join(paragraphs) if paragraphs else f"<p style='margin: 0; color: #64748b; font-size: 14px;'>{escaped_desc}</p>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Task Assigned: {safe_title}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 36px 16px;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.02); border: 1px solid #e2e8f0;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 26px 36px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-bottom: 3px solid #3b82f6;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td>
                                            <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">
                                                FAZESOFT <span style="color: #60a5fa; font-weight: 400;">EMS</span>
                                            </h1>
                                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600;">Project & Task Management</p>
                                        </td>
                                        <td align="right">
                                            <span style="display: inline-block; background-color: rgba(59, 130, 246, 0.15); border: 1px solid rgba(96, 165, 250, 0.3); color: #93c5fd; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;">
                                                Task Assigned
                                            </span>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Body Content -->
                        <tr>
                            <td style="padding: 32px 36px 24px 36px;">
                                <h2 style="margin: 0 0 8px 0; color: #0f172a; font-size: 19px; font-weight: 700;">
                                    Hello, {safe_recipient} 👋
                                </h2>
                                <p style="margin: 0 0 24px 0; color: #475569; font-size: 14px; line-height: 1.5;">
                                    A new task has been assigned to you by <strong style="color: #0f172a;">{safe_assigner}</strong> in project <strong style="color: #2563eb;">{safe_project}</strong>.
                                </p>

                                <!-- Task Detail Card -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 24px;">
                                    <tr>
                                        <td style="padding: 20px 22px;">
                                            <div style="margin-bottom: 14px;">
                                                <span style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">Task Title</span>
                                                <h3 style="margin: 4px 0 0 0; color: #0f172a; font-size: 17px; font-weight: 700;">
                                                    {safe_title}
                                                </h3>
                                            </div>

                                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top: 1px solid #e2e8f0; padding-top: 14px; font-size: 13px;">
                                                <tr>
                                                    <td style="padding: 4px 0; color: #64748b; width: 110px; font-weight: 600;">Project:</td>
                                                    <td style="padding: 4px 0; color: #0f172a; font-weight: 600;">{safe_project}</td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Priority:</td>
                                                    <td style="padding: 4px 0;">
                                                        <span style="display: inline-block; background-color: {priority_bg}; color: {priority_color}; border: 1px solid {priority_border}; font-weight: 700; font-size: 11px; padding: 2px 10px; border-radius: 12px;">
                                                            {p_upper}
                                                        </span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Deadline:</td>
                                                    <td style="padding: 4px 0; color: #b91c1c; font-weight: 700;">
                                                        📅 {safe_deadline}
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 4px 0; color: #64748b; font-weight: 600;">Assigned By:</td>
                                                    <td style="padding: 4px 0; color: #0f172a; font-weight: 600;">{safe_assigner}</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Task Description Block -->
                                <div style="margin-bottom: 28px;">
                                    <span style="display: block; color: #64748b; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; margin-bottom: 8px;">
                                        Description / Instructions
                                    </span>
                                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 18px;">
                                        {description_html}
                                    </div>
                                </div>

                                <!-- CTA Button -->
                                <div style="text-align: center; margin: 32px 0 16px 0;">
                                    <a href="{html.escape(task_url)}" target="_blank"
                                       style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; padding: 14px 34px; font-weight: 700; font-size: 14px; text-decoration: none; border-radius: 10px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); letter-spacing: 0.3px;">
                                        🚀 View Task in Dashboard
                                    </a>
                                </div>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 22px 36px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 600; color: #64748b;">
                                    FazeSoft Enterprise Management System
                                </p>
                                <p style="margin: 0 0 10px 0; font-size: 11px; color: #94a3b8;">
                                    Automated task dispatch notification &middot; Please do not reply directly to this email
                                </p>
                                <p style="margin: 0; font-size: 11px; color: #cbd5e1; line-height: 1.4;">
                                    You received this message because a task was assigned to your account ({html.escape(recipient_email)}).
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """.strip()

