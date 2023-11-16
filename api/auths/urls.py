from django.urls import path, include

from . import views as AuthView

class Register:
    urlpatterns = [
        path('', AuthView.Register.as_view({'post': 'create'}), name='register'),
        path('/check', AuthView.CheckRegister.as_view({'get': 'list'}), name='register')
    ]
    
class Verification:
    urlpatterns = [
        path('send', AuthView.SendVerification.as_view({'post': 'create'})),
        path('check', AuthView.CheckVerification.as_view({'post': 'create'})),
    ]
    
class Share:
    urlpatterns = [
        path('', AuthView.Share.as_view({'post': 'create'})),
        path('/<int:Type>', AuthView.CheckShare.as_view({'get': 'list'}))
    ]
    
class Password:
    urlpatterns = [
        path('forgot', AuthView.ForgotPassword.as_view({'post': 'create'})),
        path('reset', AuthView.ResetPassword.as_view({'post': 'create'}))
    ]
    
urlpatterns = [
    path('auth', AuthView.Login.as_view({'post': 'create'}), name='login'),
    path('register', include(Register)),
    path('verification/', include(Verification)),
    path('share', include(Share)),
    path('password/', include(Password)),
    path('news', AuthView.News.as_view({'get': 'list'}), name='news'),
]
