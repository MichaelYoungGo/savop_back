from django.urls import re_path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
import protocol.log.views as log_views
from protocol.auto_topo.views import AutoBuildTopology
from protocol.topo.views import TopologySet
from protocol.node_controller.views import NodeControllerSet
from protocol.traffic_controller.views import TrafficControllerSet
from protocol.master_controller.views import HostControllerSet
from protocol.master_controller.routing import websocket_urlpatterns

router = DefaultRouter()
router.register('topo', TopologySet, basename="topo")
router.register('node', NodeControllerSet, basename="node")
router.register('traffic', TrafficControllerSet, basename="traffic")
router.register('sav_control', HostControllerSet, basename="sav_control")

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/getNetData/$', log_views.FPathInfoView.as_view()),
    re_path(r'^api/netinfo/refresh/(?P<topo>.+)/$', log_views.RefreshTopologyProgressData.as_view(), name="netinfo_update"),
    re_path(r'^api/netinfo/(?P<topo>.+)/$', log_views.CollectTopologyProgressData.as_view(), name="netinfo"),
    re_path(r'^api/auto_build/$', AutoBuildTopology.as_view(), name="simulate_run"),
    re_path(r'^api/', include(router.urls)),
]
urlpatterns += websocket_urlpatterns

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

