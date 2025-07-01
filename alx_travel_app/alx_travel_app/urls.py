from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from django.urls import path

# from .views import PostViewSet

router = routers.DefaultRouter()
#router.register(r'users', UserViewSet)
# router.register(r'posts', PostViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

schema_view = get_schema_view(
    openapi.Info(
        title="Listings and Bookings API",
        default_version='v1',
        description="API for managing listings and bookings",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('listings.urls')),
    path('', include('listings.urls')),  # Ensure listings URLs are include
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')), 
]
