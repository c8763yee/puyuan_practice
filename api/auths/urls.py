from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views as AuthView

auth_router = DefaultRouter()
auth_router.register("register", AuthView.Register, basename="register")
auth_router.register(
    "register/check", AuthView.CheckRegister, basename="check_register"
)
auth_router.register("auth", AuthView.Login, basename="auth")
# ------------------------------------
verification_router = DefaultRouter()

verification_router.register(
    "send", AuthView.SendVerification, basename="send_verification"
)
verification_router.register(
    "check", AuthView.CheckVerification, basename="check_verification"
)

# ------------------------------------
password_router = DefaultRouter()

password_router.register("forgot", AuthView.ForgotPassword, basename="forgot_password")
password_router.register("reset", AuthView.ResetPassword, basename="reset_password")


# ------------------------------------

router = DefaultRouter()
router.register("news", AuthView.News, basename="news")
router.register("share", AuthView.Share, basename="share")

router.register(r"share/(?P<Type>\d+)", AuthView.CheckShare, basename="check_share")

router.registry.extend(auth_router.registry)
router.registry.extend(verification_router.registry)
router.registry.extend(password_router.registry)

urlpatterns = [
    path("", include(router.urls), name="auth"),
    path("verification/", include(verification_router.urls), name="verification"),
    path("password/", include(password_router.urls), name="password"),
]
