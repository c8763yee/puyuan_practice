from django.urls import path, include
from .views import UserView
from rest_framework.routers import DefaultRouter


# urlpatterns = [
#     path('register/', views.register),
#     path('auth/', views.login),
#     path('verification/send/', views.send_verification),
#     path('verification/check', views.check_verification),
#     path('password/forgot/', views.forgot_password),
#     path('password/reset/', views.reset_password),
#     path('register/check/', views.check_register),
#     path('news/', views.news),
#     path('share/', views.share),
#     path('share/<str:Type>/', views.check_share)
# ]
auth_router = DefaultRouter()
auth_router.register('register', UserView.Register, basename='register')
auth_router.register('auth', UserView.Auth, basename='login')

verification_router = DefaultRouter()

verification_router.register('send', UserView.SendVerification,
                             basename='send_verification')
verification_router.register('check', UserView.CheckVerification,
                             basename='check_verification')
# router.register('password/forgot', UserView.ForgotPassword,
#                 basename='forgot_password')
# router.register('password/reset', UserView.ResetPassword,
#                 basename='reset_password')
# router.register('register/check', UserView.CheckRegister,
#                 basename='check_register')
# router.register('news', UserView.News, basename='news')
# router.register('share', UserView.Share, basename='share')
# router.register('share/<str:Type>/', UserView.CheckShare,
#                 basename='check_share')

router = DefaultRouter()
router.registry.extend(auth_router.registry)
router.registry.extend(verification_router.registry)

urlpatterns = [
    path('', include(router.urls), name='auth'),
    path('verification/', include(verification_router.urls), name='verification')
]
