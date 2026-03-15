from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views as store_views

admin.site.site_header = "ShopNow Admin — Group 4"
admin.site.site_title = "ShopNow Admin"
admin.site.index_title = "Welcome to ShopNow Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', store_views.home, name='home'),
    path('panel/', include('dashboard.urls')),
    path('store/', include('store.urls')),
    path('accounts/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
