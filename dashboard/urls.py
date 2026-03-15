from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.dashboard_home,  name='dash_home'),
    # Products
    path('products/',                views.product_list,    name='dash_products'),
    path('products/new/',            views.product_create,  name='dash_product_create'),
    path('products/<int:pk>/edit/',  views.product_edit,    name='dash_product_edit'),
    path('products/<int:pk>/delete/',views.product_delete,  name='dash_product_delete'),
    path('products/<int:pk>/toggle/',views.product_toggle,  name='dash_product_toggle'),
    # Categories
    path('categories/',              views.category_list,   name='dash_categories'),
    path('categories/new/',          views.category_create, name='dash_category_create'),
    path('categories/<int:pk>/edit/',views.category_edit,   name='dash_category_edit'),
    path('categories/<int:pk>/delete/',views.category_delete,name='dash_category_delete'),
    # Orders
    path('orders/',                  views.order_list,      name='dash_orders'),
    path('orders/<int:pk>/',         views.order_detail,    name='dash_order_detail'),
    # Users
    path('users/',                   views.user_list,       name='dash_users'),
    path('users/<int:pk>/',          views.user_detail,     name='dash_user_detail'),
    path('users/<int:pk>/toggle/',   views.user_toggle,     name='dash_user_toggle'),
    path('users/<int:pk>/delete/',   views.user_delete,     name='dash_user_delete'),
]
