from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class ExpenseUtils:
    """Utility functions for expense-related operations"""
    
    @staticmethod
    def format_currency(amount, currency_symbol='Rp'):
        """Format amount as currency string"""
        if isinstance(amount, (int, float, Decimal)):
            return f"{currency_symbol} {amount:,.2f}"
        return f"{currency_symbol} 0.00"
    
    @staticmethod
    def calculate_percentage_change(current, previous):
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def get_date_range(period='month'):
        """Get date range for different periods"""
        now = timezone.now()
        
        if period == 'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now.replace(day=1)
        elif period == 'quarter':
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1)
        elif period == 'year':
            start_date = now.replace(month=1, day=1)
        else:
            start_date = now - timedelta(days=30)
        
        return start_date, now
    
    @staticmethod
    def get_expense_categories_colors():
        """Get predefined colors for expense categories"""
        return [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384',
            '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
        ]
    
    @staticmethod
    def validate_expense_amount(amount):
        """Validate expense amount"""
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return False, "Amount must be greater than zero"
            if amount > Decimal('999999999.99'):
                return False, "Amount is too large"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid amount format"
    
    @staticmethod
    def get_month_name(month_number):
        """Get month name from month number"""
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        if 1 <= month_number <= 12:
            return months[month_number - 1]
        return 'Unknown'
