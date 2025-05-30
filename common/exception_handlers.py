from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if not (isinstance(response.data, dict) and "detail" in response.data):
            response.data = {"error": response.data} # for example
    return response
