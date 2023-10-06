from rest_framework.metadata import BaseMetadata
from api.metadata import clone_output

EMAIL = "test@gmail.com"
PASSWORD = "1234"


class AuthMetadata:
    class Register(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL,
                        "password": PASSWORD,
                    },

                    "output": clone_output()
                }
            }

    class Auth(Register):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL,
                        "password": PASSWORD,
                    },
                    "output": clone_output(
                        {
                            "token": "Token"
                        }
                    )
                }
            }

    class SendVerification(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL
                    },
                    "output": clone_output()
                }
            }

    class CheckVerification(SendVerification):
        def determine_metadata(self, request, view):
            return {
                "GET": {
                    "input": {
                        "email": EMAIL,
                        "code": "77777"
                    },
                    "output": clone_output()
                }
            }

    class ForgotPassword(SendVerification):
        def determine_metadata(self, request, view):
            return super().determine_metadata(request, view)

    class ResetPassword(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "password": "密碼"
                    },
                    "output": clone_output()
                }
            }

    class CheckRegister(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "GET": {
                    "input": {
                        "email": EMAIL
                    },
                    "output": clone_output()
                }
            }

    class News(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "GET": {
                    "output": clone_output(
                        {
                            "news": [
                                {
                                    "id": 1,
                                    "member_id": 1,
                                    "group_id": 1,
                                    "title": "test",
                                    "message": "test",
                                    "pushed_at": "2023-08-29 16:30:30",
                                    "created_at": "2023-08-29 16:30:30",
                                    "updated_at": "2023-08-29 16:30:30"
                                }
                            ]
                        }
                    )
                }
            }

    class Share(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "type": 0,
                        "id": 1,
                        "relation_type": 1
                    },
                    "output": clone_output()
                }
            }

    class CheckShare(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "GET": {
                    "input": {
                        "type": "str(0=doctor, 1=family, 2=friend)",
                    },
                    "output": clone_output(
                        {
                            "records": {
                                "actually": "i have not idea about this field",
                            }
                        }
                    )
                }
            }
