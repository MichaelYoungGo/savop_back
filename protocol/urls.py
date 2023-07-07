from rest_framework.urls import url
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

router = DefaultRouter()
router.register('topo', TopologySet, basename="topo")
router.register('node', NodeControllerSet, basename="node")
router.register('traffic', TrafficControllerSet, basename="traffic")

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/getNetData/$', log_views.FPathInfoView.as_view()),
    url(r'^api/netinfo/refresh/(?P<topo>.+)/$', log_views.RefreshTopologyProgressData.as_view(), name="netinfo_update"),
    url(r'^api/netinfo/(?P<topo>.+)/$', log_views.CollectTopologyProgressData.as_view(), name="netinfo"),
    url(r'^api/auto_build/$', AutoBuildTopology.as_view(), name="simulate_run"),
    url(r'^api/', include(router.urls))
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

