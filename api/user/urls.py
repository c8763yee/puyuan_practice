from django.urls import path, include

from . import views as UserViewSet


# below class is use for leveling url
class Blood:
    # this is static class
    urlpatterns = [
        path("pressure", UserViewSet.BloodPressure.as_view({"post": "create"})),
        path("sugar", UserViewSet.BloodSugar.as_view({"post": "create"})),
    ]


# ------------------------------------

urlpatterns = [
    path("", UserViewSet.UserInfo.as_view({"get": "list", "patch": "partial_update"})),
    path("/default", UserViewSet.Default.as_view({"patch": "partial_update"})),
    path("/setting", UserViewSet.Setting.as_view({"patch": "partial_update"})),
    path("/blood/", include(Blood)),
    path("/weight", UserViewSet.Weight.as_view({"post": "create"})),
    path(
        "/records", UserViewSet.Record.as_view({"post": "create", "delete": "destroy"})
    ),
    path("/diary", UserViewSet.Diary.as_view({"get": "list"})),
    path("/diet", UserViewSet.Diet.as_view({"post": "create"})),
    path(
        "/a1c",
        UserViewSet.A1c.as_view({"post": "create", "get": "list", "delete": "destroy"})
    ),
    path(
        "/medical",
        UserViewSet.Medical.as_view({"get": "list", "patch": "partial_update"})
    ),
    path(
        "/drug-used",
        UserViewSet.Drug.as_view(
            {"post": "create", "get": "list", "delete": "destroy"}
        ),
    ),
    path(
        "/care",
        UserViewSet.Care.as_view({"get": "list", "post": "create"})
    ),
    path('/badge', UserViewSet.Badge.as_view({'put': 'update'}))
]
