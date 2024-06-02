
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


class DataMock(Data):
    GROUPS = []
    CABINETS = []
    TEACHERS = []
    COURSES = []
    def __init__(self):
        self.GROUPS = []
        self.CABINETS = []
        self.TEACHERS = []
        self.COURSES = []

    def load(self):
        from src import Group, Teacher, Cabinet, Course
        file = open('groups.txt','r+',encoding='utf-8')
        res = file.readlines()
        for i in res:
            self.GROUPS.append(Group(id=i.split('$')[0],name=i.split('$')[1].replace('\n','')))
        file.close()

        file = open('teachers.txt', 'r+', encoding='utf-8')
        res = file.readlines()
        for i in res:
            self.TEACHERS.append(Teacher(id=i.split('$')[0], name=i.split('$')[1].replace('\n','')))
        file.close()

        file = open('cabinets.txt', 'r+', encoding='utf-8')
        res = file.readlines()
        for i in res:
            self.CABINETS.append(Cabinet(id=i.split('$')[0], name=i.split('$')[1].replace('\n','')))
        file.close()

        file = open('courses.txt', 'r+', encoding='utf-8')
        res = file.readlines()
        for i in res:
            self.COURSES.append(Course(id=i.split('$')[0], name=i.split('$')[1].replace('\n','')))
        file.close()

        pass

class DataLoged(Data):
    GROUPS = []
    CABINETS = []
    TEACHERS = []
    COURSES = []



    def save(self):
        temp = []
        print('_____________________________________')
        for i in self.GROUPS:
            temp.append(f"{i.to_json()}\n")
        print(temp)
        file = open("groups.txt","w+",encoding='utf-8')
        file.writelines(temp)
        file.close()
        temp = []
        print('_____________________________________')
        for i in self.CABINETS:
            temp.append(f"{i.to_json()}\n")
        print(temp)
        file = open("cabinets.txt", "w+", encoding='utf-8')
        file.writelines(temp)
        file.close()
        temp = []
        print('_____________________________________')
        for i in self.TEACHERS:
            temp.append(f"{i.to_json()}\n")
        print(temp)
        file = open("teachers.txt", "w+", encoding='utf-8')
        file.writelines(temp)
        file.close()
        temp = []
        print('_____________________________________')
        for i in self.COURSES:
            temp.append(f"{i.to_json()}\n")
        file = open("courses.txt", "w+", encoding='utf-8')
        file.writelines(temp)
        file.close()
        print(temp)


    def __init__(self,sup):
        from src import getGroups, getCabinets, getTeachers, getCourses
        self.GROUPS = getGroups(sup=sup)
        self.CABINETS = getCabinets(sup=sup)
        self.TEACHERS = getTeachers(sup=sup)
        self.COURSES = getCourses(sup=sup)
