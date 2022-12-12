import psycopg2 as pg2
from psycopg2 import extensions as pg2es
import json
import get_students
from platform import uname


if uname().system == 'Windows':
        DB_CONN = pg2.connect(database='gmaraton', user='postgres', password=132005)
else:
    connect_str = "dbname='chess_users' user='lasker' host='localhost' password='132005'"
    DB_CONN = pg2.connect(connect_str)
DB_CONN.autocommit = True

NINE = 'nine'
TEN = 'ten'
ELEVEN = 'eleven'
TWELVE = 'twelve'
TABLES_NAMES = [NINE, TEN, ELEVEN, TWELVE]

CLASS = 'class'
NAME = 'name'
SURNAME = 'surname'
TEST1 = 'test1'
TEST2 = 'test2'
TEST3 = 'test3'
BONUS1 = 'bonus1'
BONUS2 = 'bonus2'
BONUS3 = 'bonus3'

ATTEND1 = 'attend1'
ATTEND2 = 'attend2'
ATTEND3 = 'attend3'
COMPETITION = 'competition'

WEIGHT = {TEST1: 0.1, TEST2: 0.3, TEST3: 0.3, BONUS1: 0, BONUS2: 0.045, BONUS3: 0.045, ATTEND1: 0.07, ATTEND2: 0.07, ATTEND3: 0.07}
BONUS_MULTIPLIER = 3

C_TYPE = 'type'
C_LEN = 'len'
C_CONSTRAINS = 'constrains'

COLUMNS = {
    CLASS:          {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    NAME:           {C_TYPE: 'varchar', C_LEN: 50, C_CONSTRAINS: 'not null'},
    TEST1:          {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    TEST2:          {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    TEST3:          {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    BONUS1:         {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    BONUS2:         {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
    BONUS3:         {C_TYPE: 'decimal', C_LEN: None, C_CONSTRAINS: 'not null'},
}

COLUMNS_L = list(COLUMNS)
TESTS = [TEST1, TEST2, TEST3]
BONUSES = [BONUS1, BONUS2, BONUS3]
ATTENDS = [ATTEND1, ATTEND2, ATTEND3]

def check_data(table, class_num=None, name=None, column=None, value=None):
    if table not in TABLES_NAMES:
        print("Table does not exist")
        return False
    if class_num:
        if not class_num.isnumeric():
            print("class_num must be an integer")
            return False
        if int(class_num) not in get_class_numbers_list(table):
            print("class_num invalid (not in class list)")
            return False
        if name:
            if name not in get_class_names(table, class_num):
                print("name invalid")
                return False
            if column:
                if column not in COLUMNS:
                    print("column does not exist")
                    return False
                if value:
                    type = get_type(column)
                    if type == 'varchar':
                        if not isinstance(value, str):
                            print("value must be a string")
                            return False
                        if get_len(column):
                            if len(value) > get_len(column):
                                print("value is too long")
                                return False
                    elif type == 'decimal':
                        if not value.isnumeric():
                            print("value must be an integer")
                            return False
                        if int(value) > 100:
                            print("value must be equal or less than 100")
                            return False
    return True


def get_len(column)->int:
    return COLUMNS[column][C_LEN]


def get_type(column)->str:
    return COLUMNS[column][C_TYPE]


def get_constrains(column)->str:
    return COLUMNS[column][C_CONSTRAINS]

def execute(code)->pg2es.cursor:
    connection = DB_CONN
    cursor = connection.cursor()
    cursor.execute(code)
    return cursor


def create_tables()->None:
    for table in TABLES_NAMES:
        columns = ""
        for column in COLUMNS:
            columns += f"{column} {get_type(column)} "
            if get_len(column):
                columns += f"({get_len(column)})"
            columns += f"{get_constrains(column)},\n"
        execute(f"create table if not exists {table}({columns[:-2]});").close()


def drop_tables()->None:
    for table in TABLES_NAMES:
        execute(f"drop table if exists {table};").close()


def reset_tables()->None:
    drop_tables()
    create_tables()
    load_database()
    set_additional_grading()


def insert_new_user(table, class_num, name):
    student = [class_num, name]
    for column in TESTS:
        if column == TEST1:
            student.append('70')
        else:
            student.append('0')
    for column in BONUSES:
        student.append('0')
    execute(f"insert into {table}({', '.join(COLUMNS_L)}) values({', '.join(student)});").close()


def get_class_names(table, class_num):
    data = execute(f"select {NAME} from {table} where {CLASS} = {class_num};").fetchall()
    return [name[0] for name in data]
    

def get_student_amount(table, class_num):
    return execute(f"select count(*) from {table} where {CLASS} = {class_num};").fetchone()[0]


def update_grade(table, class_num, name, column, new_value):
    execute(f"update {table} set {column} = '{new_value}'\
            where {CLASS} = {class_num} and {NAME} = '{name}';").close()
                

def get_bonus(table, class_num, bonus, name):
    return execute(f"select {bonus} from {table} where {CLASS} = {class_num} and {NAME} = '{name}';").fetchone()[0]


def update_bonus(table, class_num, name, bonus, new_value):
    current_bonus = get_bonus(table, class_num, bonus, name)
    new_bonus = current_bonus + new_value
    if new_bonus > 10:
        new_bonus = 10
    execute(f"update {table} set {bonus} = '{new_bonus}'\
            where {CLASS} = {class_num} and {NAME} = '{name}';").close()


def get_class_test_avg(table, class_num, test):
    test_sum = execute(f"select sum({test}) from {table} where {CLASS} = {class_num};").fetchone()[0]
    return round(test_sum / get_student_amount(table, class_num))


def get_class_score(table, class_num):
    sum = 0
    for test in TESTS:
        sum += get_class_test_avg(table, class_num, test) * WEIGHT[test]
    for bonus in BONUSES:
        sum += get_class_test_avg(table, class_num, bonus) * 10 * WEIGHT[bonus] * BONUS_MULTIPLIER
    for day in ATTENDS:   
        sum += get_attendence_percente(table, class_num, day) * 100 * WEIGHT[day]
    return sum



def get_class_numbers_list(table):
    data = execute(f"select distinct {CLASS} from {table};").fetchall()
    data = [int(i[0]) for i in data]
    return data

def get_class_count(table):
    return len(get_class_numbers_list(table))


def get_grade_score(table):
    sum = 0
    class_amount = get_class_count(table)
    for i in range(class_amount):
        sum += get_class_score(table, i + 1)
    return round(sum / class_amount)


def load_database():
    translate = {'ט': NINE, 'י': TEN, 'יא': ELEVEN, 'יב': TWELVE}
    students = get_students.load_students()
    if not isinstance(students, list):
        return False
    for student in students:
        table = translate[student['grade']]
        name = student['name'].replace("'", "")
        name = f"'{name}'"
        insert_new_user(table, student['class_num'], name)

def get_class_table(table, class_num):
    columns = [NAME] + TESTS + BONUSES
    data = execute(f"select {', '.join(columns)} from {table} where {CLASS} = {class_num};").fetchall()
    for i in range(len(data)):
        data[i] = list(data[i])
        for j in range(len(data[i])):
            if get_type(columns[j]) == 'decimal':
                data[i][j] = int(data[i][j])
    return data
    

def get_grade_table(table):
    data = {}
    class_numbers = get_class_numbers_list(table)
    for class_num in class_numbers:
        data[class_num] = get_class_table(table, class_num)
    return data


def get_school_table():
    data = {}
    for table in TABLES_NAMES:
        data[table] = get_grade_table(table)
    return data


def set_additional_grading():
    dictionary = {}
    for table in TABLES_NAMES:
        dictionary[table] = {COMPETITION : 0}
        for class_num in get_class_numbers_list(table):
            dictionary[table][class_num] = {ATTEND1 : 0, ATTEND2 : 0, ATTEND3 : 0}
    with open("additional_grades.json", "w") as outfile:
        json.dump(dictionary, outfile)


def set_attendents(table, class_num, day, attendents):
    with open("additional_grades.json", "r") as infile:
        dictionary = json.load(infile)
    dictionary[table][str(class_num)][day] = attendents
    with open("additional_grades.json", "w") as outfile:
        json.dump(dictionary, outfile)


def get_attendence_percente(table, class_num, day):
    with open("additional_grades.json", "r") as infile:
        dictionary = json.load(infile)
    amount = dictionary[table][str(class_num)][day]
    return round(amount / get_student_amount(table, class_num), 1)


def get_competition(table):
    with open("additional_grades.json", "r") as infile:
        dictionary = json.load(infile)
    return dictionary[table][COMPETITION]

def set_competition(table, new_value):
    with open("additional_grades.json", "r") as infile:
        dictionary = json.load(infile)
    dictionary[table][COMPETITION] = new_value
    with open("additional_grades.json", "w") as outfile:
        json.dump(dictionary, outfile)


def get_additional_grading():
    with open("additional_grades.json", "r") as infile:
        dictionary = json.load(infile)
    return dictionary


def main():
    # reset_tables()
    pass


if __name__ == '__main__':
    main()
