MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

TOKEN_EXPIRE_TIME = DAY  # 1 day

EMAIL = "testtiananmen7357@gmail.com"
PASSWORD = "1234"

ALL_FIELDS = "__all__"

SALT = "NUTCIMACPUYUAN"

NOT_ANSWERED = 0
ACCEPT = 1
REFUSE = 2
INVALID_TYPE = 3

DIET_LEN = 8
DIET_TIME = ["晨起", "早餐前", "早餐後", "午餐前", "午餐後", "晚餐前", "晚餐後", "睡前"]

DEFAULT_DIARY_DICT = {
    "id": 0,
    "user_id": 0,
    "systolic": 0,
    "diastolic": 0,
    "pulse": 0,
    "weight": 0.0,
    "body_fat": 0.0,
    "bmi": 0.0,
    "sugar": 0.0,
    "exercise": 0,
    "drug": 0,
    "timeperiod": 0,
    "description": "",
    "meal": 0,
    "tag": [{"name": [], "message": ""}],  # name: list[str]
    "image": ["http://www.example.com"],
    "location": {"lat": "", "lng": ""},
    "reply": "",
    "recorded_at": "",
    "type": "",
}
