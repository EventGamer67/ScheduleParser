class ParsedDate:
    def __init__(self, date, filehash, link):
        self.date = date
        # self.name = name
        self.hash = filehash
        self.link = link
        pass

    def getparams(self):
        return {'date': self.date, 'hash': self.hash, 'link': self.link}