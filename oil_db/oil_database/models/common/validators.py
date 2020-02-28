

class EnumValidator:
    def __init__(self, valid_items, err_msg):
        self._valid_items = valid_items
        self.err_msg = err_msg

    def __call__(self, item):
        if not item in self._valid_items:
            return [self.err_msg.format(item=item, valid_items=valid_items)]
        else:
            return []

