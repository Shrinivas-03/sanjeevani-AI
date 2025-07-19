import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DatabaseService:
    def __init__(self):
        url = os.getenv('supabase_url')
        key = os.getenv('supabase_key')
        self.supabase: Client = create_client(url, key)
    
    def create_user(self, full_name, email, password_hash, phone=None, date_of_birth=None, 
                   gender=None, blood_group=None, address=None):
        """
        Create a new user in the database
        """
        try:
            # Prepare data dictionary matching the users table schema
            user_data = {
                'full_name': full_name,
                'email': email.lower(),
                'password_hash': password_hash,
                'phone': phone,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'blood_group': blood_group,
                'address': address,
                'is_active': True,
                'email_verified': False
            }
            
            # Filter out None values
            user_data = {k: v for k, v in user_data.items() if v is not None}
            
            # Use Supabase API to insert the user
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data and len(result.data) > 0:
                return {
                    'id': result.data[0]['id'],
                    'email': result.data[0]['email'],
                    'full_name': result.data[0]['full_name']
                }
            return None
            
        except Exception as e:
            print(f"Database error in create_user: {str(e)}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def verify_user_email(self, email):
        """Mark user's email as verified"""
        try:
            result = self.supabase.table('users').update({
                'email_verified': True,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error verifying user: {str(e)}")
            return None
    
    def update_user_password(self, email, new_password_hash):
        """Update user's password"""
        try:
            print(f"Updating password for user: {email}")  # Debug log
            
            # Update the password_hash field in the users table
            result = self.supabase.table('users').update({
                'password_hash': new_password_hash,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('email', email).execute()
            
            print(f"Password update result: {result}")  # Debug log
            
            # Check if update was successful
            return result.data and len(result.data) > 0
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False
    
    def store_otp(self, email, otp_code, purpose='email_verification'):
        """Store OTP in database"""
        try:
            # First, delete any existing OTPs for this email
            self.supabase.table('otp_verifications').delete().eq('email', email).eq('purpose', purpose).execute()
            
            otp_data = {
                'email': email,
                'otp_code': otp_code,
                'purpose': purpose,
                'is_used': False,
                'attempts': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('otp_verifications').insert(otp_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error storing OTP: {str(e)}")
            return None
    
    def verify_otp(self, email, otp_code, purpose='email_verification'):
        """Verify OTP code"""
        try:
            # Get OTP record
            result = self.supabase.table('otp_verifications').select('*').eq('email', email).eq('otp_code', otp_code).eq('purpose', purpose).eq('is_used', False).execute()
            
            if not result.data:
                return False
            
            otp_record = result.data[0]
            
            # Check if OTP has expired (5 minutes)
            created_at = datetime.fromisoformat(otp_record['created_at'].replace('Z', '+00:00'))
            now = datetime.utcnow().replace(tzinfo=created_at.tzinfo)
            
            if (now - created_at).total_seconds() > 300:  # 5 minutes
                return False
            
            # Mark OTP as used
            self.supabase.table('otp_verifications').update({
                'is_used': True,
                'verified_at': datetime.utcnow().isoformat()
            }).eq('id', otp_record['id']).execute()
            
            return True
            
        except Exception as e:
            print(f"Error verifying OTP: {str(e)}")
            return False
    
    def increment_otp_attempts(self, email, purpose='email_verification'):
        """Increment OTP verification attempts"""
        try:
            result = self.supabase.table('otp_verifications').select('*').eq('email', email).eq('purpose', purpose).eq('is_used', False).execute()
            
            if result.data:
                otp_record = result.data[0]
                new_attempts = otp_record['attempts'] + 1
                
                self.supabase.table('otp_verifications').update({
                    'attempts': new_attempts
                }).eq('id', otp_record['id']).execute()
                
                return new_attempts
            
            return 0
            
        except Exception as e:
            print(f"Error incrementing attempts: {str(e)}")
            return 0
        
    def get_email_by_otp(self, otp_code, purpose='password_reset'):
        """Get email associated with a valid OTP"""
        try:
            print(f"Looking for OTP: {otp_code} with purpose: {purpose}")  # Debug log
            
            # Query the otp_verifications table with proper conditions
            result = self.supabase.table('otp_verifications').select('email') \
                .eq('otp_code', otp_code) \
                .eq('purpose', purpose) \
                .eq('is_used', False) \
                .lt('attempts', 3) \
                .gte('expires_at', datetime.utcnow().isoformat()) \
                .execute()
            
            print(f"OTP lookup result: {result}")  # Debug log
            
            if result.data and len(result.data) > 0:
                return result.data[0]['email']
            
            return None
        except Exception as e:
            print(f"Error getting email by OTP: {str(e)}")
            return None

    def invalidate_otp(self, email, otp_code, purpose='password_reset'):
        """Mark an OTP as used"""
        try:
            print(f"Invalidating OTP for email: {email}")  # Debug log
            
            # Mark the OTP as used in the otp_verifications table
            result = self.supabase.table('otp_verifications').update({
                'is_used': True,
                'verified_at': datetime.utcnow().isoformat()
            }).eq('email', email).eq('otp_code', otp_code).eq('purpose', purpose).execute()
            
            print(f"OTP invalidation result: {result}")  # Debug log
            
            return True
        except Exception as e:
            print(f"Error invalidating OTP: {str(e)}")
            return False
