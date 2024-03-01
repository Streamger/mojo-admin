from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser, Permission, Group
from api.managers import UserManager

class User(AbstractUser, AbstractBaseUser):
    first_name = None
    last_name = None
    is_staff = None
    is_superuser = None
    

    username = models.CharField(max_length = 255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length = 128)
    is_active = True

    #role 1 for admin
    role = models.IntegerField()

    date_joined = models.DateTimeField(auto_now_add = True)
    last_login = models.DateTimeField(auto_now_add = False, auto_now = False)

    REQUIRED_FIELDS = []

    objects = UserManager() #We can use this like new_admin = Admin.objects.create_user(username='roshan',email='example@example.com', password='password123')
 
    #  # Add related_name to avoid clashes with auth.User model
    # # to avoid clash in the reverse accessor names for the groups and user_permissions fields between your custom Admin model and the built-in auth.User model. 
    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='user_permissions')


    def __str__(self):
        return self.username
    

class Product(models.Model):
    name = models.CharField(max_length = 255)
    image = models.ImageField(upload_to="product")
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length = 255)
    def __str__(self):
        return self.name        
    
class Supplier(models.Model):
    name = models.CharField(max_length =255)
    def __str__(self):
        return self.name
    
class Ingredients(models.Model):
    name = models.CharField(max_length = 255)
    def __str__(self):
        return self.name
    
class Countries (models.Model):
    name = models.CharField(max_length =255)
    def __str__(self):
        return self.name
    
class Manufacturer (models.Model):
    name = models.CharField(max_length =255)
    def __str__(self):
        return self.name


class PurchaseTable(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    unit = models.IntegerField()    #unit=1 means we have bought  pieces of product, 
                                    # Unit >1 means we have bought cartoons of the product, and 1 cartoon has this many pieces
    quantity = models.IntegerField() #quantity is pieces if unit=1, cartoons if unit>1
    total_price = models.DecimalField(decimal_places=2, max_digits=15)
    purchase_date = models.DateTimeField(auto_now_add = True)

    supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    country_of_origin = models.ForeignKey(Countries, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)

    ingredients = models.ManyToManyField(Ingredients)

    mrp = models.DecimalField(decimal_places=2, max_digits=15)

    weight = models.CharField(max_length = 255)

    expiry = models.DateField()
    self_life = models.CharField(max_length=50)

    manufactured_date  = models.DateField()
    regd_no = models.CharField(max_length = 255)


    def clean(self):
        if not self.expiry and not self.self_life:
            raise Exception("Eiter expiry date or Self Life should be provied")
        
        if self.expiry and self.self_life:
            raise Exception("Eiter expiry date or Self Life should be provied")

    def __str__(self):
        return self.product.name
    

    

class StockTable(models.Model):
    product = models.OneToOneField(Product, on_delete = models.CASCADE)

    stock = models.IntegerField()
  
    discount_percentage = models.DecimalField(max_digits=5, decimal_places = 2, default=0.00)
    selling_price = models.DecimalField(max_digits=15, decimal_places = 2)
    

    is_archived = models.BooleanField(default=True)

    def __str__(self):
        return self.product.name




    






