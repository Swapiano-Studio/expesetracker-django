from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Expense

class ExpenseService:
    """Service class for expense-related business logic"""
    
    @staticmethod
    def get_user_expenses(user, filters=None):
        """Get expenses for a user with optional filters"""
        queryset = Expense.objects.filter(user=user)
        
        if filters:
            queryset = ExpenseService.apply_filters(queryset, filters)
        
        return queryset.order_by('-date')
    
    @staticmethod
    def apply_filters(queryset, filters):
        """Apply filters to expense queryset"""
        # Date range filter
        if filters.get('date_from'):
            queryset = queryset.filter(date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(date__lte=filters['date_to'])
        
        # Category filter
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        
        # Amount range filter
        if filters.get('amount_min'):
            queryset = queryset.filter(amount__gte=filters['amount_min'])
        
        if filters.get('amount_max'):
            queryset = queryset.filter(amount__lte=filters['amount_max'])
        
        # Search in description
        if filters.get('search'):
            search_term = filters['search']
            queryset = queryset.filter(
                Q(description__icontains=search_term) |
                Q(category__name__icontains=search_term)
            )
        
        # Sorting
        if filters.get('sort_by'):
            queryset = queryset.order_by(filters['sort_by'])
        
        return queryset
    
    @staticmethod
    def get_expense_statistics(user, expenses=None):
        """Calculate basic expense statistics for a user
        
        Args:
            user: The user to get statistics for
            expenses: Optional pre-filtered queryset of expenses. If not provided,
                     will use all user expenses.
        """
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        total_expenses = expenses.count()
        total_amount = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        avg_expense = total_amount / total_expenses if total_expenses > 0 else Decimal('0.00')
        
        return {
            'total_expenses': total_expenses,
            'total_amount': total_amount,
            'avg_expense': avg_expense
        }
    
    @staticmethod
    def get_monthly_statistics(user):
        """Get current month statistics and comparison with previous month"""
        current_month = timezone.now().replace(day=1)
        user_expenses = Expense.objects.filter(user=user)
        
        # Current month data
        next_month = current_month.replace(month=current_month.month + 1) if current_month.month < 12 else current_month.replace(year=current_month.year + 1, month=1)
        current_month_expenses = user_expenses.filter(date__gte=current_month, date__lt=next_month)
        current_month_total = current_month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        current_month_count = current_month_expenses.count()
        
        # Previous month for comparison
        if current_month.month == 1:
            prev_month = current_month.replace(year=current_month.year - 1, month=12)
        else:
            prev_month = current_month.replace(month=current_month.month - 1)
        
        prev_month_expenses = user_expenses.filter(date__gte=prev_month, date__lt=current_month)
        prev_month_total = prev_month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate percentage change
        if prev_month_total > 0:
            month_change = ((current_month_total - prev_month_total) / prev_month_total) * 100
        else:
            month_change = 100 if current_month_total > 0 else 0
        
        return {
            'current_month_total': current_month_total,
            'current_month_count': current_month_count,
            'month_change': month_change
        }
    
    @staticmethod
    def get_monthly_trends(user, expenses=None, months=12):
        """Get monthly expense trends for the last N months"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        monthly_data = expenses.filter(
            date__gte=timezone.now() - timedelta(days=365)
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        labels = [item['month'].strftime('%b %Y') for item in monthly_data]
        data = [float(item['total']) for item in monthly_data]
        
        return {'labels': labels, 'data': data}
    
    @staticmethod
    def get_category_distribution(user, expenses=None):
        """Get expense distribution by category"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        category_data = expenses.values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        category_labels = [item['category__name'] for item in category_data]
        category_amounts = [float(item['total']) for item in category_data]
        category_colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]
        
        return {
            'labels': category_labels,
            'amounts': category_amounts,
            'colors': category_colors
        }
    
    @staticmethod
    def get_weekly_trends(user, expenses=None, weeks=8):
        """Get weekly expense trends for the last N weeks"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        weekly_data = expenses.filter(
            date__gte=timezone.now() - timedelta(weeks=weeks)
        ).annotate(
            week=TruncWeek('date')
        ).values('week').annotate(
            total=Sum('amount')
        ).order_by('week')
        
        weekly_labels = [f"Week of {item['week'].strftime('%b %d')}" for item in weekly_data]
        weekly_amounts = [float(item['total']) for item in weekly_data]
        
        return {'labels': weekly_labels, 'amounts': weekly_amounts}
    
    @staticmethod
    def get_daily_trends(user, expenses=None, days=30):
        """Get daily expense trends for the last N days"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        daily_data = expenses.filter(
            date__gte=timezone.now() - timedelta(days=days)
        ).annotate(
            day=TruncDate('date')
        ).values('day').annotate(
            total=Sum('amount')
        ).order_by('day')
        
        daily_labels = [item['day'].strftime('%m/%d') for item in daily_data]
        daily_amounts = [float(item['total']) for item in daily_data]
        
        return {'labels': daily_labels, 'amounts': daily_amounts}
    
    @staticmethod
    def get_top_categories(user, expenses=None, limit=5):
        """Get top categories by expense count"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        
        return expenses.values('category__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def get_recent_expenses(user, expenses=None, limit=5):
        """Get recent expenses for quick view"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
        return expenses.order_by('-date')[:limit]

    @staticmethod
    def get_chart_data(user, expenses=None):
        """Get all chart data for the dashboard"""
        if expenses is None:
            expenses = Expense.objects.filter(user=user)
            
        return {
            'monthly': ExpenseService.get_monthly_trends(user, expenses),
            'weekly': ExpenseService.get_weekly_trends(user, expenses),
            'daily': ExpenseService.get_daily_trends(user, expenses),
            'category': ExpenseService.get_category_distribution(user, expenses)
        }
    
    @staticmethod
    def export_expenses_to_csv(user, queryset=None):
        """Export user expenses to CSV format"""
        import csv
        from io import StringIO
        from django.utils import timezone
        
        # If no queryset provided, get all user expenses
        if queryset is None:
            queryset = Expense.objects.filter(user=user).order_by('-date')
        
        # Create CSV file in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow([
            'Date',
            'Category',
            'Amount',
            'Description',
            'Created At',
            'Updated At'
        ])
        
        # Write data rows
        for expense in queryset:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                expense.category.name,
                str(expense.amount),
                expense.description or '',
                expense.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                expense.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return output.getvalue()
