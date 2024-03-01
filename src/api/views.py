
import datetime
from django.shortcuts import render

from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken

from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F

from urllib.parse import urljoin

from api import serializers

from api.models import Product
from api.permissions import AdminPermission


from api.models import Product, PurchaseTable
from api.models import Supplier,Category,Countries,Ingredients, Manufacturer
from api.models import StockTable

# Create your views here.

class Login(APIView):
    permission_classes = [AllowAny]
    login_data = serializers.LoginSerializer
    def post(self,request):
        try:
            user_data = self.login_data(data=request.data,partial=True)
            user_data.is_valid(raise_exception=True)
            data = user_data.validated_data

            # if data.get('user_name') and data.get('password'):

            admin = authenticate(username=data.get('username'), password= data.get('password'))

            if not admin:
                raise Exception("Employee not found")
            
            admin.last_login = timezone.now()
            admin.save()
            payload = {"role":admin.role}
            employee_detail = {
                "user_name":admin.username,
                "email":admin.email
            }
            refresh = RefreshToken.for_user(admin)
            refresh.payload.update(payload)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)


                


            return Response({"success":True,
                             "detail":employee_detail,
                             "token":{"access_token":access_token,"refresh_token":refresh_token}})
        except Exception as e:
            return Response({"success":False,"message":str(e)})


class ProductView(APIView):

    permission_classes=[AdminPermission]
    product_serializer = serializers.ProductInfoSerializer

    def post(self, request):
        try:

            proudct_data = self.product_serializer(data=request.data)
            proudct_data.is_valid(raise_exception=True)

            data = proudct_data.validated_data

            if Product.objects.filter(name=data.get('name')).exists():
                raise Exception("Product already exists")
            
            product_instance = Product.objects.create(name = data.get('name').lower(),image=data.get('image'))
            product_instance.save()

            # print(settings.MEDIA_URL)
            return Response({"success":True,"name": product_instance.name, "image":urljoin(settings.MEDIA_URL,str(product_instance.image))})
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    
    def get (self, request):
        try:
            search_query = request.query_params.get('search_query')
            if not search_query:
                product_instance = Product.objects.all()
            else:
                product_instance = Product.objects.filter(name__icontains = serializers)

            paginator = Paginator(product_instance, 10)
            page_number = request.query_params.get('page_number')
            final_product_instance = paginator.get_page(page_number)

            product_data = [{
                    "name":product.name,
                    "image":urljoin(settings.MEDIA_URL,str(product.image)),
                    "stock":StockTable.objects.get(product=product).stock if StockTable.objects.filter(product=product) else ""
                    } for product in final_product_instance]

            return Response({"success":True,"data":product_data})
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    
    def delete(self,request):
        try:
            product_id = request.query_params.get('product_id')
            if not Product.objects.filter(id= product_id).exists():
                raise Exception("This Product does not exists")
            
            
            product_instance = Product.objects.get(id=product_id)
            
            product_name = product_instance.name

            product_instance.image.delete(save=False)
            product_instance.delete()

            return Response({"success":True,"name":product_name})
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    
    def patch(self,request):
        try:
            product_id = request.query_params.get('product_id')

            if not Product.objects.filter(id= product_id).exists():
                raise Exception("This Product does not exists")
            
            proudct_data = self.product_serializer(data=request.data, partial=True)
            proudct_data.is_valid(raise_exception=True)

            data = proudct_data.validated_data

            product_instance = Product.objects.get(id=product_id)

            product_instance.name = data.get('name', product_instance.name).lower()

            if data.get('image'):
                product_instance.image.delete(save=False)
                product_instance.image = data.get('image', product_instance.image)

            product_instance.save()


            return Response ({"success":True,"name": product_instance.name, "image":urljoin(settings.MEDIA_URL,str(product_instance.image))})
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        

class Purchase(APIView):
    
    permission_classes=[AdminPermission]
    purchase_serializer = serializers.PurchaseSerializer
    stock_serializer = serializers.StockSerializer

    def post(self, request):
        try:

            product_serializer = self.purchase_serializer(data=request.data)
            product_serializer.is_valid(raise_exception=True)
            data = product_serializer.validated_data

            stock_serializer = self.stock_serializer(data=request.data)
            stock_serializer.is_valid(raise_exception=True)
            stock_data = stock_serializer.validated_data


            
            product_name = data.get('name',"")
            unit_name = data.get('unit',"")
            quantity_name = data.get('quantity','')
            total_price_name = data.get('total_price',"")
            mrp_name = data.get('mrp', "")
            weight_name = data.get('weight',"")
            expiry_name = data.get('expiry',"")
            self_life_name = data.get('self_life',"")
            manufactured_date_name= data.get('manufactured_date',"")
            regd_no_name = data.get('regd_no',"")

            supplier_name = data.get('supplier',"")
            category_name = data.get('category',"")
            country_name = data.get('country_of_origin',"")
            manufacturer_name = data.get('manufacturer',"")

            ingredients_name = data.get('ingredients',[])

           
            # print(quantity_name, unit_name)
            stock_name = quantity_name if unit_name==1 else unit_name*quantity_name
            discount_name = stock_data.get('discount_percentage','')[0] if isinstance(stock_data.get('discount_percentage',''),tuple) and len(stock_data.get('discount_percentage',''))>0 else stock_data.get('discount_percentage','')
            
            selling_name = round(mrp_name - (discount_name/100)*mrp_name,2)
         
            is_archive_name = stock_data.get('is_archived', True)



            with transaction.atomic():

                if not Product.objects.filter(name=product_name).exists():
                    product_instance = Product.objects.create(name = data.get('name').lower(),image=data.get('image'))
                    product_instance.save()

                product_instance = Product.objects.get(name=product_name)

                # print(supplier_name)

                supplier_instance, _ = Supplier.objects.get_or_create(name=supplier_name)
                category_instance, _ = Category.objects.get_or_create(name=category_name)
                country_instance, _ = Countries.objects.get_or_create(name=country_name)
                manufacturer_name, _ = Manufacturer.objects.get_or_create(name=manufacturer_name)

                # print(expiry_name)
                purchase_instance = PurchaseTable.objects.create(
                    product= product_instance,

                    unit = unit_name,
                    quantity = quantity_name,
                    total_price = total_price_name,
                    mrp = mrp_name,
                    weight = weight_name,
                    expiry = expiry_name,
                    self_life = self_life_name,
                    manufactured_date = manufactured_date_name,
                    regd_no = regd_no_name,

                    supplier = supplier_instance,
                    category=category_instance,
                    country_of_origin= country_instance,
                    manufacturer = manufacturer_name
                )

                # print(ingredients_name, data)

                ingredients_instances = [Ingredients.objects.get_or_create(name=name)[0] for name in ingredients_name]
                purchase_instance.ingredients.add(*ingredients_instances)  # * unpacks the list of ingredient instance and all the ingredients instance to the ingredients file of the purchase_instance

                purchase_instance.save()

                # print(stock_name, selling_name, discount_name, )
                if not StockTable.objects.filter(product=product_instance).exists():
                    print("here")
                    stock_instance = StockTable.objects.create(
                        product=product_instance,
                        stock = stock_name,
                        discount_percentage = discount_name,
                        selling_price = selling_name,
                        is_archived = is_archive_name
                    )
                    stock_instance.save()
                else:
                    stock_instance = StockTable.objects.get(product=product_instance)
               
                    stock_instance.stock = stock_instance.stock+stock_name
                    stock_instance.discount_percentage = discount_name
                    stock_instance.selling_price = selling_name
                    stock_instance.is_archived = is_archive_name
                    stock_instance.save()

            return Response({"success":True})
        except Exception as e:
            return Response({"success":False,"message":str(e)})

    def get(self,request):
        try:

            category_query = request.query_params.get('category')
            search_query = request.query_params.get('search_query')

            # stock_instance = StockTable.objects.all()

            # if category_query:
            #     stock_instance= StockTable.objects.filter(product__purchasetable__category__name=category_query)

            # if search_query:
            #     stock_instance = StockTable.objects.filter(product__name__icontains = search_query)

            # product_instance = stock_instance.annotate(
            #     purchase_id = F('product__purchasetable__id'),
            #     name = F('product__name'),
            #     image = F('product__image'),
            #     category = F('product__purchasetable__category__name'),
            #     weight = F('product__purchasetable__weight'),
            #     mrp = F('product__purchasetable__mrp'),
            # ).distinct('product__id')
                
            # product_data = [{

            #     "id":product["id"],
            #     "product_id":product["product_id"],
            #     "purchase_id":product["product_id"],
            #     "name":product['name'],
            #     "image":urljoin(settings.MEDIA_URL,str(product['image'])),
            #     "category":product['category'],
            #     "weight":product['weight'],
            #     "mrp":product['mrp'],
            #     "selling_price":product['selling_price']
            #     } for product in product_instance.values()]
            
            

            # # print(product_instance.values())
            # for data in product_instance.values():
            #     print(data)

            purchase_instance = PurchaseTable.objects.all()

            if search_query:
                purchase_instance = PurchaseTable.objects.filter(product__name__icontains = search_query)

            print(purchase_instance[0].product.image)
            
            purchase_data = [{
                "purchase_id":purchase.id,
                "product_id":purchase.product.id,
                "name":purchase.product.name,
                "image":urljoin(settings.MEDIA_URL,str(purchase.product.image)),
                "unit":purchase.unit,
                "quantity":purchase.quantity,
                "total_price":purchase.total_price,
                "purchase_date":purchase.purchase_date,
                "supplier_name":purchase.supplier.name,
                "category":purchase.category.name,
                "country_of_origin":purchase.country_of_origin.name,
                "manufacturer":purchase.manufacturer.name,
                "ingredients":[ingredients.name for ingredients in purchase.ingredients.all()],
                "mrp":purchase.mrp,
                "weight":purchase.weight,
                "expiry_date":purchase.expiry,
                "self_life":purchase.self_life,
                "manufactured_date":purchase.manufactured_date,
                "registration_name":purchase.regd_no

            } for purchase in purchase_instance]

            
            return Response({"success":True,"purchase_data":purchase_data})
        except Exception as e:
            return Response({"success": True})
        
    
    def delete(self, request):
        try:

            purchased_id = request.query_params.get('purchase_id')
            
            if not PurchaseTable.objects.filter(id=purchased_id).exists():
                raise Exception("This purchase id does not exists")
            
            stock_instance = StockTable.objects.get(product__purchasetable__id=purchased_id)
            purchase_instance = PurchaseTable.objects.get(id=purchased_id)

            deleted= purchase_instance.product.name

            with transaction.atomic():
                stock_instance.stock = stock_instance.stock - purchase_instance.unit*purchase_instance.quantity
                stock_instance.save()

                purchase_instance.ingredients.clear()
                purchase_instance.delete()

            
            return Response({"success":True,"deletd":deleted})
        except Exception as e:
            return Response({"success":False,"message":str(e)})
        
    
    def patch(self,request):
        try:
            purchase_id = request.query_params.get('purchase_id')
            product_id = request.query_params.get('product_id')

            if product_id is not None:
                product_instance = Product.objects.get(ide=product_id)
            else:
                product_instance = Product.objects.get(purchasetable__id = purchase_id)

            if not PurchaseTable.objects.filter(id=purchase_id).exists():
                raise Exception("This purchase id does not exists")
            
            purchase_instance = PurchaseTable.objects.get(id=purchase_id)
            stock_instance = StockTable.objects.get(product__purchasetable__id=purchase_id)

            purchase_serializer = self.purchase_serializer(data=request.data,context= {"request":request}, partial=True)
            purchase_serializer.is_valid(raise_exception=True)
            data = purchase_serializer.validated_data
            
            

            supplier_instance,_ = Supplier.objects.get_or_create(name=data.get('supplier',purchase_instance.supplier.name).lower())
            category_instance,_ = Category.objects.get_or_create(name = data.get('category',purchase_instance.category.name).lower())
            manufacturer_instnace,_ = Manufacturer.objects.get_or_create(name = data.get('manufacturer', purchase_instance.manufacturer.name).lower())
            country_instance,_  = Countries.objects.get_or_create(name=data.get('country_of_origin',purchase_instance.country_of_origin.name).lower())


            print("here")

            with transaction.atomic():

                if data.get('unit') and data.get('quantity'):
                    stock_instance.stock = stock_instance.stock -purchase_instance.unit*purchase_instance.quantity + data.get('unit')*data.get('quantity')
                    stock_instance.save()

                purchase_instance.product = product_instance
                purchase_instance.unit = data.get('unit',purchase_instance.unit)
                purchase_instance.quantity = data.get('quantity', purchase_instance.quantity)
                purchase_instance.total_price = data.get('total_price', purchase_instance.total_price)
                purchase_instance.purchase_date = data.get('purchase_date',purchase_instance.purchase_date)
                purchase_instance.supplier = supplier_instance if supplier_instance else purchase_instance.supplier
                purchase_instance.category = category_instance
                purchase_instance.country_of_origin = country_instance
                purchase_instance.manufacturer = manufacturer_instnace
                purchase_instance.mrp = data.get('mrp', purchase_instance.mrp)
                purchase_instance.weight = data.get('weight', purchase_instance.weight).lower()
                purchase_instance.expiry = data.get('expiry',purchase_instance.expiry)
                purchase_instance.self_life = data.get('self_life',purchase_instance.self_life)
                purchase_instance.manufactured_date = data.get('manufactured_date', purchase_instance.manufactured_date)
                purchase_instance.regd_no = data.get('regd_no',purchase_instance.regd_no)

                print("hellooooooo")
                ingredients_instances = [Ingredients.objects.get_or_create(name=name)[0] for name in data.get('ingredients',[ingredients.name for ingredients in purchase_instance.ingredients.all()])]
                purchase_instance.ingredients.set(ingredients_instances)  # * unpacks the list of ingredient instance and all the ingredients instance to the ingredients file of the purchase_instance

                purchase_instance.save()

            data_to_be_sent={
                "name":purchase_instance.product.name,
                "unit":purchase_instance.unit,
                "quantity":purchase_instance.quantity,
                "total_price":purchase_instance.total_price,
                "purchase_date":purchase_instance.purchase_date,
                "supplier":purchase_instance.supplier.name,
                "category":purchase_instance.category.name,
                "country_of_origin":purchase_instance.country_of_origin.name,
                "manufacturer":purchase_instance.manufacturer.name 
            }

            return Response({"success":True, "data":data_to_be_sent})
        except Exception as e:
            return Response({"success":False,"message":str(e)})