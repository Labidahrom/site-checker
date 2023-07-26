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
    path('add_urls/', views.CreateUrls.as_view(), name='add_urls'),
    path('<int:pk>/update/', views.UpdateUrl.as_view(), name='update_url'),
    path('<int:pk>/delete/', views.DeleteUrl.as_view(), name='delete_url'),
    path('parse_urls/', views.PrepareUrlsData.as_view(), name='parse_urls'),
    path('parse_urls_list/', views.PreparedUrlsList.as_view(), name='parse_urls_list'),
    path('check_text/', views.CheckText.as_view(), name='check_text'),
    path('check_text_list/', views.CheckTextList.as_view(), name='check_text_list'),
]
