# farms/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SoilTypeViewSet,
    CropTypeViewSet,
    FarmViewSet,
    PlotViewSet,
    FarmImageViewSet,
    FarmSensorViewSet,
    FarmIrrigationViewSet,
)

router = DefaultRouter()
router.register('soil-types',       SoilTypeViewSet,        basename='soiltype')
router.register('crop-types',       CropTypeViewSet,        basename='croptype')
router.register('farms',            FarmViewSet,            basename='farm')
router.register('plots',            PlotViewSet,            basename='plot')
router.register('farm-images',      FarmImageViewSet,       basename='farmimage')
router.register('farm-sensors',     FarmSensorViewSet,      basename='farmsensor')
router.register('farm-irrigations', FarmIrrigationViewSet,  basename='farmirrigation')

urlpatterns = [
    path('', include(router.urls)),
]
