BASE_OUTPUT = {
    "status": "0=成功; 1=失敗",
    "message": "成功; 失敗"
}


def clone_output(additional: dict = {}):
    return {**BASE_OUTPUT, **additional}
