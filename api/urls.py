from django.urls import path, include
from . import views

urlpatterns = [
    path('/', include('api.auths.urls'))
    # path('user/', include('api.body.urls')),
    # path('friend/', include('api.friend.urls'))
]
