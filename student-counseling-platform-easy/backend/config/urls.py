from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns=[
 path('admin/',admin.site.urls),
 path('api/schema/',SpectacularAPIView.as_view(),name='schema'),
 path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui'),
 path('api/auth/',include('accounts.auth_urls')),
 path('api/',include('accounts.urls')),
 path('api/',include('counseling.urls')),
 path('api/dashboard/',include('dashboard.urls')),
]
