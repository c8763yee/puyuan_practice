BASE_OUTPUT = {"status": "0=成功; 1=失敗", "message": "成功; 失敗"}
EXPECT_DATA = {"input": {}, "output": BASE_OUTPUT}


def clone_output(additional: dict = {}):
    return {**BASE_OUTPUT, **additional}


def get_input_output(output: dict = {}, **kwargs):
    _return_dict = {}
    if "input" in kwargs:
        inputs = kwargs["input"]
        _return_dict["input"] = inputs
    _return_dict["output"] = clone_output(output)
    return _return_dict


def process_method(
    **kwargs,
) -> dict:
    return_dict = {}
    for method in ["GET", "POST", "UPDATE", "PATCH", "PUT", "DELETE"]:
        payload = kwargs.get(method, {})
        if not payload:
            continue

        return_dict.update({method: get_input_output(**payload)})
    return return_dict


def setup_response(header: dict = {}, **method):
    _return_dict = {"Header": header, **process_method(**method)}
    if not header:
        del _return_dict["Header"]
    return _return_dict
