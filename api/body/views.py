from django.shortcuts import render

# Create your views here.


def user(request):  # METHOD: [PATCH, GET]
    # check if request method is PATCH using request.method
    if request.method not in {"PATCH", "GET"}:
        return {"error": "Method not allowed"}, 405

    if request.method == 'PATCH':
        pass
    elif request.method == 'GET':
        pass
