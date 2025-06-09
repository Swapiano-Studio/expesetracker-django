from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

class UserUtils:
    """Utility functions for user-related operations"""
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength
        Returns (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
            
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
            
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
            
        return True, None
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format and uniqueness
        Returns (is_valid, error_message)
        """
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format"
            
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return False, "Email already exists"
            
        return True, None
    
    @staticmethod
    def get_user_type_display(user_type):
        """Get display name for user type"""
        user_types = {
            'admin': 'Administrator',
            'staff': 'Staff Member',
            'user': 'Regular User'
        }
        return user_types.get(user_type, 'Unknown')
    
    @staticmethod
    def get_job_display(job):
        """Get display name for job"""
        jobs = {
            'civil_servant': 'Civil Servant',
            'private_employee': 'Private Employee',
            'entrepreneur': 'Entrepreneur',
            'student': 'Student',
            'other': 'Other'
        }
        return jobs.get(job, 'Unknown')
    
    @staticmethod
    def get_income_display(income):
        """Get display name for income range"""
        income_ranges = {
            '<1m': 'Less than 1 Million IDR',
            '1-3m': '1 - 3 Million IDR',
            '3-5m': '3 - 5 Million IDR',
            '5-10m': '5 - 10 Million IDR',
            '>10m': 'More than 10 Million IDR'
        }
        return income_ranges.get(income, 'Unknown')
    
    @staticmethod
    def format_address(country, city, address):
        """Format full address from components"""
        parts = []
        if address:
            parts.append(address)
        if city:
            parts.append(city)
        if country:
            parts.append(country)
        
        return ', '.join(parts) if parts else 'No address provided'
