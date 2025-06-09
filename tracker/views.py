from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime

from .view_helpers import ExpenseViewHelper, get_dashboard_context

def home(request):
    """Home page with expense dashboard or guest dashboard"""
    if request.user.is_authenticated:
        # Handle POST requests (add, edit, delete expense)
        if request.method == 'POST':
            helper = ExpenseViewHelper(request)
            result = helper.handle_expense_form_submission()
            
            # If result is a redirect, return it
            if hasattr(result, 'status_code'):
                return result
            
            # If result contains form errors, we'll handle them in the context
            if isinstance(result, dict):
                context = get_dashboard_context(request)
                context.update(result)
                return render(request, 'tracker/home.html', context)
            elif result:  # Form with errors
                context = get_dashboard_context(request)
                context['expense_form'] = result
                return render(request, 'tracker/home.html', context)
        
        # Handle GET requests
        context = get_dashboard_context(request)
        return render(request, 'tracker/home.html', context)
    else:
        # Guest user sees guest dashboard
        return render(request, 'tracker/guest_dashboard.html')

@login_required
def export_expenses_csv(request):
    """Export user expenses to CSV file"""
    helper = ExpenseViewHelper(request)
    expense_data = helper.get_filtered_expenses()
    
    # Generate CSV content
    csv_content = helper.expense_service.export_expenses_to_csv(request.user, expense_data['expenses'])
    
    # Create HTTP response with CSV content
    response = HttpResponse(csv_content, content_type='text/csv')
    
    # Generate filename with current date
    filename = f"expenses_{request.user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    
    return response

def about(request):
    """About page view"""
    return render(request, 'tracker/about.html', {'now': datetime.now()})

def guest_dashboard(request):
    """Empty dashboard for guests (not logged in users)"""
    return render(request, 'tracker/guest_dashboard.html')
