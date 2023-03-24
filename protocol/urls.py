from rest_framework.urls import url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
import protocol.log.views as log_views
from protocol.auto_topo.views import AutoBuildTopology


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/getNetData/$', log_views.FPathInfoView.as_view()),
    url(r'^api/netinfo/refresh/(?P<topo>.+)/$', log_views.RefreshTopologyProgressData.as_view()),
    url(r'^api/netinfo/(?P<topo>.+)/$', log_views.CollectTopologyProgressData.as_view()),
    url(r'^api/auto_build/$', AutoBuildTopology.as_view()),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

