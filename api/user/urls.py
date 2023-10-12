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
    path('weight/', UserViewSet.Weight.as_view({'post': 'create'})),
    path('blood/sugar/', UserViewSet.BloodSugar.as_view({'post': 'create'})),
    path('records/',
         UserViewSet.Record.as_view({'post': 'create', 'delete': 'destroy'})),
    path('diary/', UserViewSet.Diary.as_view({'get': 'list'})),
]
