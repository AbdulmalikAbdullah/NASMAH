import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    @staticmethod
    def send_password_reset(user, reset_token):
        """Builds and sends the password reset email via SMTP."""
        smtp_host = os.environ.get('SMTP_HOST')
        if not smtp_host:
            print("⚠ SMTP_HOST not configured. Email not sent.")
            return False
            
        try:
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"
            
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            smtp_user = os.environ.get('SMTP_USER')
            smtp_pass = os.environ.get('SMTP_PASS')
            use_tls = os.environ.get('SMTP_USE_TLS', '1') in ['1', 'true', 'True']
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Password reset instructions'
            msg['From'] = os.environ.get('SMTP_FROM') or smtp_user or 'no-reply@lungcancerai.com'
            msg['To'] = user.email

            # HTML Email Body
            html_body = f"""
            <p>Hello {user.Fname},</p>
            <p>To reset your password <a href="{reset_link}">click here</a>.</p>
            <p>If you didn't request this, ignore this email.</p>
            """
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if use_tls:
                server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)

            server.sendmail(msg['From'], [user.email], msg.as_string())
            server.quit()
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False