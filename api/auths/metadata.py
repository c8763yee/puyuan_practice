from rest_framework.metadata import BaseMetadata

from api.metadata import setup_response

from puyuan.const import EMAIL, PASSWORD


class Register(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            POST={
                "input": {
                    "email": EMAIL,
                    "password": PASSWORD,
                },
            }
        )


class Auth(Register):
    def determine_metadata(self, request, view):
        return setup_response(
            POST={
                "input": {
                    "email": EMAIL,
                    "password": PASSWORD,
                },
                "output": {
                    "token": "token",
                },
            }
        )


class SendVerification(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            POST={
                "input": {"email": EMAIL},
            }
        )


class CheckVerification(SendVerification):
    def determine_metadata(self, request, view):
        return setup_response(
            POST={
                "input": {"email": EMAIL, "code": ""},
            }
        )


class ForgotPassword(SendVerification):
    def determine_metadata(self, request, view):
        return super().determine_metadata(request, view)


class ResetPassword(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorization": "Bearer ${token}"},
            POST={"input": {"password": "密碼"}},
        )


class CheckRegister(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(GET={"input": {"email": EMAIL}})


class News(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorization": "Bearer ${token}"},
            GET={
                "output": {
                    "news": [
                        {
                            "id": 1,
                            "member_id": 1,
                            "group_id": 1,
                            "title": "test",
                            "message": "test",
                            "pushed_at": "2023-08-29 16:30:30",
                            "created_at": "2023-08-29 16:30:30",
                            "updated_at": "2023-08-29 16:30:30",
                        }
                    ]
                }
            },
        )


class Share(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorization": "Bearer ${token}"},
            POST={
                "input": {"type": 0, "id": 1, "relation_type": 1},
            },
        )


class CheckShare(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorization": "Bearer ${token}"},
            GET={
                "input": {
                    "type": "str(0=doctor, 1=family, 2=friend)",
                },
                "output": {
                    "records": {
                        "actually": "i have not idea about this field",
                    }
                },
            },
        )
