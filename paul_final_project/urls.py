from django.contrib import admin
from django.urls import path, include

# Wire up the admin site and then delegate all novel-related URLs
# to the novels app so this root config stays small
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('novels.urls')),
]
