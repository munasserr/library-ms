from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is not None and not isinstance(data, dict):
            data = {"detail": data}
        elif isinstance(data, dict) and "detail" not in data:
            data = {"detail": data}
        return super().render(data, accepted_media_type, renderer_context)
