"""ITMP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from tmp import  views
from django.urls import path,re_path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),
    path('home/', views.home),

#'''********** 系统菜单 **********''',
     re_path(r'^(?i)afSys/$', views.af_sys),


    path('queryAFCase/', views.query_af_case),




#'''********** 系统管理 **********''',
   re_path(r'^(?i)sysManage/$', views.sys_manage),
   re_path(r'^(?i)createSys/$', views.create_sys),
   re_path(r'^(?i)deleteSys/$', views.delete_sys),
   re_path(r'^(?i)editSys/$', views.edit_sys),
   re_path(r'^(?i)querySys/$', views.query_sys),




#'''********** 用户管理 **********''',
    re_path(r'^(?i)userManage/$', views.user_manage),
    re_path(r'^(?i)createUser/$', views.create_user),


#'''********** 公用 **********''',
    path('buildCase/', views.build_case),

    path('exportCase/', views.export_case),
    path('downloadReport/', views.download_report),

    path('saveTestInfo/', views.save_test_info),
    path('getTestReport/', views.get_test_report),
    path('caseExeStatus/', views.case_exe_status),
    path('querySysRelease/', views.query_sys_release),


#'''********** 测试 **********''',
    path('test/', views.test),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
