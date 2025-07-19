import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('smtp_server')
        self.smtp_port = int(os.getenv('smtp_port'))
        self.email_user = os.getenv('email')
        self.email_password = os.getenv('email_password')
        
    def send_otp_email(self, recipient_email, otp_code, user_name=None):
        """Send OTP verification email"""
        try:
            # Create message using MIMEMultipart instead of MIMEText
            message = MIMEMultipart("alternative")
            message["Subject"] = "Sanjeevani AI - Email Verification"
            message["From"] = self.email_user
            message["To"] = recipient_email
            
            # Create HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ color: #2c7a7b; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .otp-code {{ background-color: #2c7a7b; color: white; font-size: 24px; font-weight: bold; padding: 15px 30px; border-radius: 8px; text-align: center; margin: 20px 0; letter-spacing: 3px; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">SANJEEVANI AI</div>
                        <h2>Email Verification</h2>
                    </div>
                    
                    <p>Hello{' ' + user_name if user_name else ''},</p>
                    
                    <p>Thank you for registering with Sanjeevani AI. To complete your registration, please verify your email address using the OTP code below:</p>
                    
                    <div class="otp-code">{otp_code}</div>
                    
                    <p><strong>This code will expire in 5 minutes.</strong></p>
                    
                    <p>If you didn't request this verification, please ignore this email.</p>
                    
                    <div class="footer">
                        <p>This is an automated message from Sanjeevani AI. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text = f"""
            SANJEEVANI AI - Email Verification
            
            Hello{' ' + user_name if user_name else ''},
            
            Thank you for registering with Sanjeevani AI. To complete your registration, please verify your email address using the OTP code below:
            
            OTP Code: {otp_code}
            
            This code will expire in 5 minutes.
            
            If you didn't request this verification, please ignore this email.
            """
            
            # Convert to MimeText objects
            text_part = MIMEText(text, "plain")
            html_part = MIMEText(html, "html")

            # Add parts to message
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_password_reset_email(self, recipient_email, reset_token, user_name=None):
        """Send password reset email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Sanjeevani AI - Password Reset"
            message["From"] = self.email_user
            message["To"] = recipient_email

            reset_link = f"http://127.0.0.1:5000/auth/reset-password?token={reset_token}"

            # Create HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ color: #2c7a7b; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .reset-button {{ display: inline-block; background-color: #2c7a7b; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">SANJEEVANI AI</div>
                        <h2>Password Reset Request</h2>
                    </div>
                    
                    <p>Hello{' ' + user_name if user_name else ''},</p>
                    
                    <p>We received a request to reset your password. Click the button below to reset your password:</p>
                    
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="reset-button">Reset Password</a>
                    </p>
                    
                    <p>This link will expire in 1 hour for security reasons.</p>
                    
                    <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                    
                    <div class="footer">
                        <p>This is an automated message from Sanjeevani AI. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text = f"""
            SANJEEVANI AI - Password Reset Request
            
            Hello{' ' + user_name if user_name else ''},
            
            We received a request to reset your password. Click the link below to reset your password:
            
            {reset_link}
            
            This link will expire in 1 hour for security reasons.
            
            If you didn't request a password reset, please ignore this email.
            """
            
            # Convert to MimeText objects
            text_part = MIMEText(text, "plain")
            html_part = MIMEText(html, "html")

            # Add parts to message
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
