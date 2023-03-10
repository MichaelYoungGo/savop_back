from rest_framework.urls import url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
import savnet.log.views as log_views
from savnet.auto_topo.views import SavnetAutoBuildTopology


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/getNetData/$', log_views.FPathInfoView.as_view()),
    url(r'^api/netinfo/(?P<topo>.+)/$', log_views.CollectSavnetTopologyProgressData.as_view()),
    url(r'^api/auto_build/$', SavnetAutoBuildTopology.as_view()),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

