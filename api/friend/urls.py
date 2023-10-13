from django.urls import path, include

from . import views as AuthView


class AcceptOrRefuse:
    urlpatterns = [
        path(
            "accept/",
            AuthView.Accept.as_view({"get": "list"}),
            name="accept_Invitation",
        ),
        path(
            "refuse/",
            AuthView.Refuse.as_view({"get": "list"}),
            name="refuse_Invitation",
        ),
    ]
    pass


urlpatterns = [
    path("code/", AuthView.Code.as_view({"get": "list"}), name="code"),
    path("list/", AuthView.List.as_view({"get": "list"}), name="list"),
    path("requests/", AuthView.Requests.as_view({"get": "list"}), name="requests"),
    path("send/", AuthView.Send.as_view({"post": "create"}), name="send"),
    path("<int:inviteid>/", include(AcceptOrRefuse)),
    path("remove/", AuthView.Remove.as_view({"delete": "destroy"}), name="remove"),
    path("results/", AuthView.Results.as_view({"get": "list"}), name="result"),
]
