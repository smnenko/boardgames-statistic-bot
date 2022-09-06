class IDsOptionUtil:

    def __init__(self,  ids: list = None, options: list = None, ids_option: list = None):
        self.ids = ids
        self.options = options

        if not ids_option:
            self.ids_option = [[i, options[0]] for i in ids]
        else:
            self.ids_option = ids_option

    def get_next_option(self, option):
        ind = self.options.index(option)
        return (
            self.options[ind + 1]
            if ind < len(self.options) - 1
            else self.options[0]
        )

    def get_ids_option(self, id_):
        next_ids_option = []
        for i, j in self.ids_option:
            if id_ == i:
                next_ids_option.append([i, self.get_next_option(j)])
            else:
                next_ids_option.append([i, j])

        return IDsOptionUtil(ids_option=next_ids_option, options=self.options)

    def __iter__(self):
        return iter(self.ids_option)

    @classmethod
    def from_str(cls, string, options=None):
        ids_option = []
        for i in string.split('_'):
            ids_option.append(list(map(lambda x: int(x), i.split(':'))))

        return cls(ids_option=ids_option, options=options)

    def to_str(self):
        return '_'.join(f'{i}:{j}' for i, j in self.ids_option)
