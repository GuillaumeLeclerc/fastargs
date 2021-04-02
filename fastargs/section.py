from .state import get_current_config

class Section:
    def __init__(self, ns, desc=None,
                 config_descriptor=None):
        self.ns = tuple(ns.split('.'))

        if config_descriptor is None:
            config_descriptor = get_current_config()
        self.config_descriptor = config_descriptor

        self.desc = desc

        self.config_descriptor.add_section(self)

    def params(self, **kwargs):
        for name, param in kwargs.items():
            self.config_descriptor.add_entry(self.ns, name, param)
        return self


