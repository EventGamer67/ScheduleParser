class Subscriber:
    def __init__(self, id,token ,clientID,subType, subID ):
        self.id = id
        self.token = token
        self.clientID = clientID
        self.subType = subType
        self.subID = subID

    def __repr__(self):
        return f"Sub(id={self.id}, token='{self.token}')"

    def to_json(self):
        return f"{self.id}${self.token}"