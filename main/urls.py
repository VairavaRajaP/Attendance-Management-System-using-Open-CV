"""DjangoAttendance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('facedata/<int:staff_id>/', views.user_face, name='facedata'),
    path('details/', views.details, name='details'),
    path('details/teachers/', views.details_teachers, name='details_teachers'),
    path('profile/teacher/add/', views.add_teacher, name='add_teacher'),
    path('profile/delete/teacher/', views.delete_teacher, name='delete_teacher'),
    path('profile/teacher/<int:staff_id>/', views.profile_teacher, name='profile_teacher'),
    path('staffs/', views.staff_list, name='staff_list'),
    path('report/', views.attend_details, name='attend_details'),
    # path('download/', views.download, name='download'),
    path('absent_report/', views.ab_attend_details, name='ab_attend_details'),
    path('report/teachers/', views.attend_details_list, name='attend_details_list'),
    path('absent_report/teachers/', views.ab_attend_details_list, name='ab_attend_details_list'),
    # path('download/excel/', views.download_as_excel, name='download_as_excel'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/<int:staff_id>/<int:date_id>/', views.attendance_detail, name='attendance_detail'),
    path('staffs/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('staffs/date/', views.date, name='date_detail'),

    # path('<str:filepath>/', views.download_file, name='download_file'),
    # path('report/', views.results, name='results'),
    # url(r'^pdf/(?P<staff_id>[0-9]+)/$', views.GeneratePdf.as_view(), name='generatepdf'),
    # path('pdf/10/', views.GeneratePdf.as_view(), name='generatepdf'),

]
