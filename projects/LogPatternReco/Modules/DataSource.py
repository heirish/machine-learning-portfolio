
class DataSource:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise ValueError("data_source only accept dictionary")
        self.data = data

    def getTextFromId(self, id):
        return self.data[id]

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def addItem(self, id, text):
        if not id or id in self.data.keys():
            return False
        else:
            self.data[id] = text
            return True



