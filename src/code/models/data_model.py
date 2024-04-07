
class Data:

    GROUPS = []
    CABINETS = []
    TEACHERS = []
    COURSES = []
    def __init__(self,sup):
        from src import getGroups, getCabinets, getTeachers, getCourses
        self.GROUPS = getGroups(sup=sup)
        self.CABINETS = getCabinets(sup=sup)
        self.TEACHERS = getTeachers(sup=sup)
        self.COURSES = getCourses(sup=sup)