from django.urls import path
from novels import views

# uses the path:s3_key converter so keys with forward slashes such as moby_dick.txt are captured correctly
urlpatterns = [
    path('', views.novel_list, name='novel_list'),
    path('novel/<path:s3_key>/analyze/', views.novel_analyze, name='novel_analyze'),
    path('novel/<path:s3_key>/tts/', views.novel_tts, name='novel_tts'),
    path('novel/<path:s3_key>/', views.novel_detail, name='novel_detail'),
]
