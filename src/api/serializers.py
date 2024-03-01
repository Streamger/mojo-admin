from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from django.contrib.auth import get_user_model

User = get_user_model()


class ProductInfoSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(required= True)


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')

        if not User.objects.filter(username=username).exists():
            raise Exception("User not found")
        
        return attrs
    

class PurchaseSerializer(serializers.Serializer):
    
    name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)

    unit = serializers.IntegerField(required = True)
    quantity = serializers.IntegerField(required = True)
    total_price = serializers.DecimalField(decimal_places=2,required = True,  max_digits=15)
    purchase_date = serializers.DateTimeField(required = False)

    supplier = serializers.CharField(required = True)
    category = serializers.CharField(required = True)
    ingredients =serializers.ListField(required = True)
    country_of_origin = serializers.CharField(required = True)

    mrp = serializers.DecimalField(decimal_places=2, required = True, max_digits=15)
    weight = serializers.CharField(required = True)

    expiry = serializers.DateField(required = False)
    self_life = serializers.CharField(required = False)

    manufactured_date  = serializers.DateField(required = True)
    manufacturer = serializers.CharField(required=True)
    regd_no = serializers.CharField(required = True)

    def validate(self, attrs):

        request = self.context.get('request')
        is_partial = request and request.method in ("PATCH")
        print(is_partial, request)
        if is_partial:
            print("hello")
            return attrs

        name = attrs.get('name')
        image = attrs.get('image')

        expiry = attrs.get('expiry')
        self_life = attrs.get('self_life')

        if (name is None) != (image is None):
            raise Exception("You have to enter both name and image")
        
        if not expiry and not self_life:
            raise Exception("Eiter expiry date or Self Life should be provied")
        
        if expiry and self_life:
            raise Exception("Eiter expiry date or Self Life should be provied")

        return attrs
    

class StockSerializer(serializers.Serializer):
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places = 2, required=False)
    is_archived = serializers.BooleanField(required=False)