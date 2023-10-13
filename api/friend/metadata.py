from rest_framework.metadata import BaseMetadata
from api.metadata import setup_response


class Code(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            GET={
                "output": {"status": "0=成功; 1=失敗", "message": "成功; 失敗"},
            },
        )


class List(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            GET={
                "output": {"friends": [{"id": 1, "name": "", "relation_type": 0}]},
            },
        )


class Requests(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            GET={
                "output": {
                    "requests": [
                        {
                            "id": 1,
                            "user_id": 2,
                            "relation_id": 1,
                            "type": 0,
                            "status": 0,
                            "read": 0,
                            "created_at": "2017-10-20 15:46:16",
                            "updated_at": "2017-10-20 15:49:20",
                            "user": {"id": 2, "name": "", "account": "fb_2"},
                        }
                    ]
                },
            },
        )


class Send(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            POST={
                "input": {"type": 0, "invite_code": "55688"},
            },
        )


class Accept(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            GET={
                "input": {"inviteid": 1},
            },
        )


class Refuse(Accept):
    def determine_metadata(self, request, view):
        return super().determine_metadata(request, view)


class Remove(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            DELETE={
                "input": {"ids": [1, 2, 3]},
            },
        )


class Result(BaseMetadata):
    def determine_metadata(self, request, view):
        return setup_response(
            header={"Authorizer": "Bearer ${token}"},
            GET={
                "output": {
                    "result": [
                        {
                            "id": 1,
                            "user_id": 2,
                            "relation_id": 1,
                            "type": 0,
                            "status": 0,
                            "read": 0,
                            "created_at": "2017-10-20 15:46:16",
                            "updated_at": "2017-10-20 15:49:20",
                            "relation": {"id": 2, "name": "", "account": "fb_2"},
                        }
                    ]
                },
            },
        )
