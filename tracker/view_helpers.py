"""
Helper functions for views to make them more modular and maintainable.
"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal

from .models import Expense
from .forms import ExpenseForm, ExpenseFilterForm
from .services import ExpenseService


class ExpenseViewHelper:
    """Helper class for expense-related view operations"""
    
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.expense_service = ExpenseService()
    
    def handle_expense_form_submission(self):
        """Handle POST requests for expense operations"""
        if self.request.method != 'POST':
            return None
            
        action = self.request.POST.get('action')
        
        if action == 'add_expense':
            return self._handle_add_expense()
        elif action == 'edit_expense':
            return self._handle_edit_expense()
        elif action == 'delete_expense':
            return self._handle_delete_expense()
        
        return None
    
    def _handle_add_expense(self):
        """Handle adding new expense"""
        form = ExpenseForm(self.request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = self.user
            expense.save()
            messages.success(self.request, 'Expense added successfully!')
            return redirect('home')
        else:
            messages.error(self.request, 'Please correct the errors below.')
            return form
    
    def _handle_edit_expense(self):
        """Handle editing existing expense"""
        expense_id = self.request.POST.get('expense_id')
        expense = get_object_or_404(Expense, pk=expense_id, user=self.user)
        form = ExpenseForm(self.request.POST, instance=expense)
        
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Expense updated successfully!')
            return redirect('home')
        else:
            messages.error(self.request, 'Please correct the errors below.')
            return {'form': form, 'edit_expense': expense}
    
    def _handle_delete_expense(self):
        """Handle deleting expense"""
        expense_id = self.request.POST.get('expense_id')
        expense = get_object_or_404(Expense, pk=expense_id, user=self.user)
        expense.delete()
        messages.success(self.request, 'Expense deleted successfully!')
        return redirect('home')
    
    def get_expense_form_context(self):
        """Get form context for GET requests"""
        edit_id = self.request.GET.get('edit')
        edit_expense = None
        expense_form = None
        
        if edit_id:
            edit_expense = get_object_or_404(Expense, pk=edit_id, user=self.user)
            expense_form = ExpenseForm(instance=edit_expense)
        else:
            expense_form = ExpenseForm()
        
        return {
            'expense_form': expense_form,
            'edit_expense': edit_expense
        }
    
    def get_filtered_expenses(self):
        """Get filtered expenses based on request parameters"""
        filter_form = ExpenseFilterForm(self.request.GET)
        filters = {}
        
        if filter_form.is_valid():
            filters = {
                'date_from': filter_form.cleaned_data.get('date_from'),
                'date_to': filter_form.cleaned_data.get('date_to'),
                'category': filter_form.cleaned_data.get('category'),
                'amount_min': filter_form.cleaned_data.get('amount_min'),
                'amount_max': filter_form.cleaned_data.get('amount_max'),
                'search': filter_form.cleaned_data.get('search'),
                'sort_by': filter_form.cleaned_data.get('sort_by')
            }
        
        expenses = self.expense_service.get_user_expenses(self.user, filters)
        
        return {
            'expenses': expenses,
            'filter_form': filter_form
        }
    
    def get_statistics_context(self, expenses):
        """Get statistics context for dashboard"""
        return self.expense_service.get_expense_statistics(self.user, expenses)
    
    def get_chart_data_context(self, expenses):
        """Get chart data context"""
        return self.expense_service.get_chart_data(self.user, expenses)


import json

def get_dashboard_context(request):
    """Get complete dashboard context"""
    helper = ExpenseViewHelper(request)
    
    # Get filtered expenses
    expense_data = helper.get_filtered_expenses()
    expenses = expense_data['expenses']
    
    # Get form context
    form_context = helper.get_expense_form_context()
    
    # Get statistics
    stats_context = helper.get_statistics_context(expenses)
    
    # Get chart data
    chart_context = helper.get_chart_data_context(expenses)
    
    # Get monthly statistics
    monthly_stats = helper.expense_service.get_monthly_statistics(request.user)
    
    # Combine all contexts
    context = {
        'now': timezone.now(),
        **expense_data,
        **form_context,
        **stats_context,
        **monthly_stats,
        'category_labels': json.dumps(chart_context['category']['labels']),
        'category_amounts': json.dumps(chart_context['category']['amounts']),
        'category_colors': json.dumps(chart_context['category']['colors'])
    }
    
    return context
