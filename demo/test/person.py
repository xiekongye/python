import json


class Person:
    """Person类"""
    def __init__(self, name, age):
        """构造函数"""
        self.name = name
        self.age = age

    def __eq__(self, other):
        """判断两个对象是否相等"""
        if self.age == other.age and self.name == other.name:
            return True
        else:
            return False

    def __str__(self):
        return 'My name is : ' + self.name + ', and my age is : ' + str(self.age)

    def display(self):
        try:
            print('name : ' + self.name + ", age : " + str(self.age))
            value = 100 / self.age
            print(value)
        except ZeroDivisionError:
            print('Param illegal')
        else:
            print('Print done')


class Student(Person):
    """Person子类"""
    def __init__(self, name, age, clazz, school):
        Person.__init__(self, name, age)
        self.clazz = clazz
        self.school = school


def print_person(persons):
    print("Person in system:")
    for person in persons:
        person.display()


if __name__ == "__main__":
    me = Person('xiekongye', 29)
    you = Person('xinjinping', 59)
    they = Person('jiangzemin', 0)

