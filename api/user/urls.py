from django.urls import path, include

from .views import UserViewSet


# ------------------------------------

urlpatterns = [
    path(
        '', UserViewSet.UserInfo.as_view({'get': 'list', 'patch': 'partial_update'})),
    path('default/', UserViewSet.Default.as_view({'patch': 'partial_update'})),
    path('setting/', UserViewSet.Setting.as_view({'patch': 'partial_update'})),
    path('blood/pressure/',
         UserViewSet.BloodPressure.as_view({'post': 'create'})),
]
