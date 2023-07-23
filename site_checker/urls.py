from django.contrib import admin
from django.urls import path
from site_checker import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('urls/', views.UrlsList.as_view(), name='url_list'),
    path('checks/', views.ChecksList.as_view(), name='checks_list'),
    path('start_checks/', views.CheckUrl.as_view(), name='start_checks'),
    path('add_url/', views.CreateUrl.as_view(), name='add_url'),
    path('add_urls/', views.CreateUrls.as_view(), name='add_urls'),
    path('parse_urls/', views.ParseUrls.as_view(), name='parse_urls'),
    path('parse_urls_list/', views.ParsedUrlsList.as_view(), name='parse_urls_list'),
]
