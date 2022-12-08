import json
# the file containes a list of dictionaries, each dictionary is a student
# in the format {"A": surname, "B": name, "C": class, "D": class_num}

def load_students():
    with open('students.txt', encoding='utf8') as f:
        students = json.load(f)
    students_list = []
    for student in students:
        name = f"{student['B']} {student['A']}"
        grade = student['C']
        class_num = str(student['D'])
        students_list.append({'grade': grade, 'class_num': class_num, 'name': name})
    return students_list
