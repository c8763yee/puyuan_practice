from rest_framework.metadata import BaseMetadata

EMAIL = "test@gmail.com"
PASSWORD = "1234"


class UserMetadata:
    class Register(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL,
                        "password": "string"
                    },

                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class Auth(Register):
        def determine_metadata(self, request, view):
            payload = super().determine_metadata(request, view)
            payload['POST']['output'].update(
                {'token': 'string(only if success)'}
            )
            return payload

    class SendVerification(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class CheckVerification(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL,
                        "code": "77777"
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class ForgotPassword(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "POST": {
                    "input": {
                        "email": EMAIL
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class ResetPassword(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "sessionid=$token"
                },
                "POST": {
                    "input": {
                        "email": EMAIL,
                        "code": "77777",
                        "password": PASSWORD
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class CheckRegister(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "GET": {
                    "input": {
                        "email": EMAIL
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class News(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer $token"
                },
                "GET": {
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail",
                        "news": [
                            {
                                "id": "int",
                                "member_id": "int",
                                "group": "int",
                                "title": "string",
                                "message": "string",
                                "pushed_at": "datetime",
                                "created_at": "datetime",
                                "updated_at": "datetime"
                            }
                        ]
                    }
                }
            }

    class Share(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer $token"
                },
                "POST": {
                    "input": {
                        "type": "int(0=blood pressure, 1=weight, 2=blood glucose, 3=diet)",
                        "id": "int",
                        "relation_type": "int(0=family, 1=friend)",
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail"
                    }
                }
            }

    class ChechShare(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer $token"
                },
                "GET": {
                    "input": {
                        "type": "str(0=doctor, 1=family, 2=friend)",
                    },
                    "output": {
                        "status": "0=success, 1=fail",
                        "message": "success, fail",
                        "records": {
                            "actually": "i have not idea about this field",
                        }
                    }
                }
            }
