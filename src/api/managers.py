from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        if not username:
            raise ValueError("Username must be set")
        
        email = self.normalize_email(email)

        user = self.model(email=email, username=username, **extra_fields)  #Similar to Model.object.create()

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using = self.db)

        return user
    

    def create_admin(self, email, username, password, **extra_fields):
        
        if not email:
            raise ValueError("Email must be set")
        if not username:
            raise ValueError("Username must be set")
        
        email = self.normalize_email(email)
    
        admin = self.model(email=email, username=username, **extra_fields)
      
        admin.set_password(password)

        admin.save(using=self.db)

        return admin
        
    