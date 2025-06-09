from django import forms
from django.forms.widgets import DateInput, NumberInput, Select, Textarea
from django.utils import timezone
from .models import Expense, ExpenseCategory

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date']
        widgets = {
            'date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'amount': NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter amount (e.g. 100.50)',
            }),
            'category': Select(attrs={
                'class': 'form-select',
            }),
            'description': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes or details about this expense (optional)',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        self.fields['description'].required = False
        self.fields['description'].label = 'Description (Optional)'
        self.fields['category'].label = 'Category'
        self.fields['amount'].label = 'Amount'
        self.fields['date'].label = 'Date'

class ExpenseFilterForm(forms.Form):
    """Form for filtering and searching expenses"""
    
    # Date range filters
    date_from = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'From date'
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'To date'
        }),
        label='To Date'
    )
    
    # Category filter
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=Select(attrs={
            'class': 'form-select'
        }),
        label='Category'
    )
    
    # Amount range filters
    amount_min = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Min amount'
        }),
        label='Min Amount'
    )
    
    amount_max = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        widget=NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Max amount'
        }),
        label='Max Amount'
    )
    
    # Search in description
    search = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in descriptions...'
        }),
        label='Search'
    )
    
    # Sorting options
    SORT_CHOICES = [
        ('-date', 'Date (Newest First)'),
        ('date', 'Date (Oldest First)'),
        ('-amount', 'Amount (Highest First)'),
        ('amount', 'Amount (Lowest First)'),
        ('category__name', 'Category (A-Z)'),
        ('-category__name', 'Category (Z-A)'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-date',
        widget=Select(attrs={
            'class': 'form-select'
        }),
        label='Sort By'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        amount_min = cleaned_data.get('amount_min')
        amount_max = cleaned_data.get('amount_max')
        
        # Validate date range
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("From date cannot be later than to date.")
        
        # Validate amount range
        if amount_min and amount_max and amount_min > amount_max:
            raise forms.ValidationError("Minimum amount cannot be greater than maximum amount.")
        
        return cleaned_data
