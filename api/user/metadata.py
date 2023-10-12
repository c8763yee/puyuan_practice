from rest_framework.metadata import BaseMetadata
from api.metadata import clone_output


class UserMetadata:
    class User(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "GET": {
                    "input": {
                    },
                    "output": clone_output({
                        "id": 1,
                        "name": "王小明",
                        "account": "test@gmail.ocm",
                        "email": "test@gmail.ocm",
                        "phone": "0987987987",
                        "fb_id": "未設置",
                        "status": "VIP",
                        "group": "0",
                        "birthday": "2023-08-29",
                        "height": 187,
                        "weight": "87",
                        "gender": 0,
                        "address": "台中市北區三民路三段129號",
                        "unread_records": [
                            0,
                            0,
                            0
                        ],
                        "verified": 0,
                        "privacy_policy": 1,
                        "must_change_password": 1,
                        "fcm_id": "",
                        "login_times": 0,
                        "created_at": "2023-08-23 16:51:14",
                        "updated_at": "2023-08-23 16:51:14",
                        "default": {
                            "id": 1,
                            "user_id": 1,
                            "sugar_delta_max": None,
                            "sugar_delta_min": None,
                            "sugar_morning_max": None,
                            "sugar_morning_min": None,
                            "sugar_evening_max": None,
                            "sugar_evening_min": None,
                            "sugar_before_max": None,
                            "sugar_before_min": None,
                            "sugar_after_max": None,
                            "sugar_after_min": None,
                            "systolic_max": None,
                            "systolic_min": None,
                            "diastolic_max": None,
                            "diastolic_min": None,
                            "pulse_max": None,
                            "pulse_min": None,
                            "weight_max": None,
                            "weight_min": None,
                            "bmi_max": None,
                            "bmi_min": None,
                            "body_fat_max": None,
                            "body_fat_min": None,
                            "created_at": "2023-08-23 16:51:14",
                            "updated_at": "2023-08-23 16:51:14"
                        },
                        "setting": {
                            "id": 1,
                            "user_id": 1,
                            "after_recording": 0,
                            "no_recording_for_a_day": 0,
                            "over_max_or_under_min": 0,
                            "after_meal": 0,
                            "unit_of_sugar": 0,
                            "unit_of_weight": 0,
                            "unit_of_height": 0,
                            "created_at": "2023-02-03 08:17:17",
                            "updated_at": "2023-02-03 08:17:17"
                        },
                        "vip": {
                            "id": 1,
                            "user_id": 1,
                            "level": 0,
                            "remark": 0.0,
                            "started_at": "2023-02-03 08:17:17",
                            "ended_at": "2023-02-03 08:17:17",
                            "created_at": "2023-02-03 08:17:17",
                            "updated_at": "2023-02-03 08:17:17",
                        }
                    })
                },
                "PATCH": {
                    "input": {
                        "name": "王小明",
                        "birthday": "2023-08-29",
                        "height": 187,
                        "weight": "87",
                        "phone": "0987987987",
                        "email": "test@gmail.com",
                        "gender": True,
                        "fcm_id": "1234",
                        "address": "台中市北區三民路三段129號",
                    },
                    "output": clone_output()
                }
            }

    class Default(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "PATCH": {
                    "input": {
                        "sugar_delta_max": 10.0,
                        "sugar_delta_min": 1.0,
                        "sugar_morning_max": 10.0,
                        "sugar_morning_min": 1.0,
                        "sugar_evening_max": 10.0,
                        "sugar_evening_min": 1.0,
                        "sugar_before_max": 10.0,
                        "sugar_before_min": 1.0,
                        "sugar_after_max": 10.0,
                        "sugar_after_min": 1.0,
                        "systolic_max": 10,
                        "systolic_min": 1,
                        "diastolic_max": 10,
                        "diastolic_min": 1,
                        "pulse_max": 10,
                        "pulse_min": 1,
                        "weight_max": 10.0,
                        "weight_min": 1.0,
                        "bmi_max": 10.0,
                        "bmi_min": 1.0,
                        "body_fat_max": 10.0,
                        "body_fat_min": 1.0
                    },
                    "output": clone_output()
                }
            }

    class Setting(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "PATCH": {
                    "input": {
                        "after_recording": False,
                        "no_recording_for_a_day": False,
                        "over_max_or_under_min": True,
                        "after_meal": True,
                        "unit_of_sugar": True,
                        "unit_of_weight": True,
                        "unit_of_height": True

                    },
                    "output": clone_output()
                }
            }

    class BloodPressure(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "systolic": 100,
                        "diastolic": 100,
                        "pulse": 60,
                        "Recorded_at": "2023-02-03 08:17:17"
                    },
                    "output": clone_output(
                        {"records": "success, fail"}
                    )
                }
            }

    class Weight(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "weight": 87.0,
                        "body_fat": 23.0,
                        "bmi": 23.0,
                        "recorded_at": "2023-02-03 08:17:17"
                    },
                    "output": clone_output(
                        {"records": "success, fail"}
                    )
                }
            }

    class BloodSugar(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "sugar": 123.0,
                        "timeperiod": 1,
                        "recorded_at": "2023-02-03 08:17:17",
                        "drug": 1,
                        "exercise": 1
                    },
                    "output": clone_output()
                }
            }

    class Record(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "input": {
                        "diet": 0
                    },
                    "output": clone_output(
                        {
                            "blood_sugar": {
                                "sugar": 0.0
                            },
                            "blood_pressure": {
                                "systolic": 345,
                                "diastolic": 345,
                                "pulse": 345
                            },
                            "weight": {
                                "weight": 0.0
                            }
                        }
                    )
                }
            }

    class Diary(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "GET": {
                    "input": {
                        "date": "2023-09-21"
                    },
                    "output": clone_output(
                        {
                            "diary": [
                                {
                                    "id": 1,
                                    "user_id": 1,
                                    "systolic": 140,
                                    "diastolic": 139,
                                    "pulse": 117,
                                    "weight": 0.0,
                                    "body_fat": 0.0,
                                    "bmi": 0.0,
                                    "sugar": 0.0,
                                    "exercise": 0,
                                    "drug": 0,
                                    "timeperiod": 0,
                                    "description": "",
                                    "meal": 3,
                                    "tag": [
                                        {
                                            "name": ["abc"],
                                            "message": ""
                                        }
                                    ],
                                    "image": [""],
                                    "location": {
                                        "lat": "",
                                        "lng": ""
                                    },
                                    "reply": "",
                                    "recorded_at": "2023-09-21 00:06:14",
                                    "type": "blood_pressure"
                                }
                            ]
                        }
                    )
                },
            }

    class Diet(BaseMetadata):
        def determine_metadata(self, request, view):
            return {
                "Header": {
                    "Authorization": "Bearer ${token}"
                },
                "POST": {
                    "description": "good",
                    "meal": 0,
                    "tag": ["dinner"],
                    "image": 1,
                    "lat": 120.5,
                    "lng": 323.5,
                    "recorded_at": "2023-09-21 00:06:14"
                }
            }
