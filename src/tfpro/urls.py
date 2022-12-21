"""tfpro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from django.conf.urls import url
# from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

# import tfclass.views
from tfclass import views as tfv
# from rgclass import views as rgv
# from rgclassMMTen import views as rgmtv
from stclass import views as stv

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', stv.rgClassifyForm),
    path('result/', stv.rgClassifyResult),
    
# version that inlcude OSN
#   path('', rgv.rgClassifyForm),
#   path('result/', rgv.rgClassifyResult),

    path('PADv1/', tfv.tfClassifyForm),
    path('PADv1/instruction/', tfv.tfClassifyGuide),
    path('PADv1/result/', tfv.tfClassifyResult),
    
    url(r'^PADv1/download/(?P<file_name>.*)$', tfv.download),
    url(r'^download/(?P<file_name>.*)$', stv.download)

# version that use mm10 Emission regions reported by other people
#    path('PADmm10/', rgmtv.rgClassifyForm),
#    path('PADmm10/result/', rgmtv.rgClassifyResult),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
