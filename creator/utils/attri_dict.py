import os


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = AttrDict(value)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = AttrDict(value)
        self[key] = value
        if isinstance(value, (str, int, float)):
            os.environ[key] = value
        elif isinstance(value, bool):
            os.environ[key] = str(value).lower()

    def __delattr__(self, key):
        if key in self:
            del self[key]
