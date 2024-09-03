from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 기본 URL 요청에 대해 index 뷰 호출
]
