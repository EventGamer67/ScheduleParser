class ParsedDate:
    def __init__(self, date, name, filehash, link):
        self.date = date
        self.name = name
        self.hash = filehash
        self.link = link
        pass

    def getparams(self):
        return {'date': self.date, 'name': self.name, 'hash': self.hash, 'link': self.link}