from django.contrib import admin
from django.urls import path, include  # add include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # use include() with string reference
]