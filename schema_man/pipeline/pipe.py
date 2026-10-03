class Pipe:

    def __init__(self, filters):
        self.filters = filters

    def run(self, context):
        for f in self.filters:
            context = f.apply(context)
        return context
