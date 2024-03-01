from api.models import User
from django.utils import timezone

user_name = input("Enter admin name: ")
email = input ("Enter admin email: ")
password = input("Enter admin password: ")
role = input('1 for admin')
last_login = timezone.now()

admin_instance = User.objects.create_admin(username=user_name, email=email, password=password, role=role, last_login=last_login)
admin_instance.save()

#  exec(open('api/create_admin.py').read())