from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


from .views import index, boxes, faq, my_rent, order_api
from storage_app import views

urlpatterns = [
    path('', index, name='index'),
    path('boxes', boxes, name='boxes'),
    path('faq', faq, name='faq'),
    path('my-rent', my_rent, name='my_rent'),
    path('users/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('api-auth/', include('rest_framework.urls')),
    path('order', order_api, name='order'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
