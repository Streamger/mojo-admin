from django.urls import path

from .views import Login,ProductView, Purchase
from django.conf.urls.static import static

from django.conf import settings


urlpatterns = [
    path('login/',Login.as_view(),name='login'),
    path('product/',ProductView.as_view(), name='product'),
    path('purchase/',Purchase.as_view(),name='purchase')
]