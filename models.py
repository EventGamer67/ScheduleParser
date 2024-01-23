class ParsedDate:
    def __init__(self, date, name, filehash, link):
        self.date = date
        self.name = name
        self.hash = filehash
        self.link = link
        pass

    def getparams(self):
        return {'date': self.date, 'name': self.name, 'hash': self.hash, 'link': self.link}

class Group:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Group(id={self.id}, name='{self.name}')"


class Course:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Course(id={self.id}, name='{self.name}')"

class Teacher:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Teacher(id={self.id}, name='{self.name}')"

class Cabinet:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Cabinet(id={self.id}, name='{self.name}')"