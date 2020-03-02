

class EnumValidator:
    def __init__(self, valid_items, err_msg, case_insensitive=False):
        if case_insensitive:
            valid_items = [item.lower() for item in valid_items]
        self.valid_items = valid_items
        self.err_msg = err_msg
        self.case_insensitive = case_insensitive

    def __call__(self, item):
        if self.case_insensitive:
            item = item.lower()
        if not item in self.valid_items:
            return [self.err_msg.format(item, self.valid_items)]
        else:
            return []

