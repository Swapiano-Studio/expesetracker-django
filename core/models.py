from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    )
    JOB_CHOICES = (
        ('civil_servant', 'Civil Servant'),
        ('private_employee', 'Private Employee'),
        ('entrepreneur', 'Entrepreneur'),
        ('student', 'Student'),
        ('other', 'Other'),
    )
    INCOME_CHOICES = (
        ('<1m', '< 1 Million IDR'),
        ('1-3m', '1 - 3 Million IDR'),
        ('3-5m', '3 - 5 Million IDR'),
        ('5-10m', '5 - 10 Million IDR'),
        ('>10m', '> 10 Million IDR'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    job = models.CharField(max_length=20, choices=JOB_CHOICES, blank=True, null=True)
    income = models.CharField(max_length=10, choices=INCOME_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
        
# This code defines a custom user model for a Django application.
# It extends the AbstractUser model to include additional fields such as user type, job, income, email, country, city, and address.
# The user type can be admin, staff, or user, and the job and income fields have predefined choices.
# The email field is unique, ensuring no two users can have the same email address.
# The country, city, and address fields are optional and can be left blank.
# The __str__ method returns the username of the user, which is useful for displaying user objects in the admin interface or other parts of the application.
# This custom user model allows for more flexibility and customization in user management within the Django application.
