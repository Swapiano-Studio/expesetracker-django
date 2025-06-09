from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tracker.models import Expense, ExpenseCategory
from tracker.services import ExpenseService
from tracker.view_helpers import ExpenseViewHelper
from decimal import Decimal
from datetime import date

class ExpenseServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = ExpenseCategory.objects.create(name='Food')
        Expense.objects.create(user=self.user, category=self.category, amount=Decimal('10.00'), date=date.today(), description='Lunch')
        Expense.objects.create(user=self.user, category=self.category, amount=Decimal('20.00'), date=date.today(), description='Dinner')

    def test_get_user_expenses(self):
        expenses = ExpenseService.get_user_expenses(self.user)
        self.assertEqual(expenses.count(), 2)

    def test_apply_filters(self):
        filters = {'amount_min': Decimal('15.00')}
        expenses = ExpenseService.apply_filters(Expense.objects.filter(user=self.user), filters)
        self.assertEqual(expenses.count(), 1)
        self.assertEqual(expenses.first().amount, Decimal('20.00'))

    def test_get_expense_statistics(self):
        stats = ExpenseService.get_expense_statistics(self.user)
        self.assertEqual(stats['total_expenses'], 2)
        self.assertEqual(stats['total_amount'], Decimal('30.00'))
        self.assertEqual(stats['avg_expense'], Decimal('15.00'))

    def test_export_expenses_to_csv(self):
        csv_data = ExpenseService.export_expenses_to_csv(self.user)
        self.assertIn('Lunch', csv_data)
        self.assertIn('Dinner', csv_data)

class ExpenseViewHelperTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.category = ExpenseCategory.objects.create(name='Food')

    def test_handle_add_expense(self):
        response = self.client.post(reverse('home'), {
            'action': 'add_expense',
            'category': self.category.id,
            'amount': '15.00',
            'date': date.today(),
            'description': 'Snack'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Expense.objects.filter(description='Snack').exists())

    def test_handle_edit_expense(self):
        expense = Expense.objects.create(user=self.user, category=self.category, amount=Decimal('10.00'), date=date.today(), description='Lunch')
        response = self.client.post(reverse('home'), {
            'action': 'edit_expense',
            'expense_id': expense.id,
            'category': self.category.id,
            'amount': '12.00',
            'date': date.today(),
            'description': 'Lunch updated'
        })
        self.assertEqual(response.status_code, 302)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, Decimal('12.00'))
        self.assertEqual(expense.description, 'Lunch updated')

    def test_handle_delete_expense(self):
        expense = Expense.objects.create(user=self.user, category=self.category, amount=Decimal('10.00'), date=date.today(), description='Lunch')
        response = self.client.post(reverse('home'), {
            'action': 'delete_expense',
            'expense_id': expense.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expense.objects.filter(id=expense.id).exists())

class ViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.category = ExpenseCategory.objects.create(name='Food')
        Expense.objects.create(user=self.user, category=self.category, amount=Decimal('10.00'), date=date.today(), description='Lunch')

    def test_home_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/home.html')
        self.assertIn('expenses', response.context)

    def test_export_expenses_csv(self):
        response = self.client.get(reverse('export_expenses_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        self.assertIn('Lunch', response.content.decode())

