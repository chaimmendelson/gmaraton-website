//format should be: {'grade': 'nine', 'class': 1, 'name': 'chaim', 'column': 'test1', 'value': 100}
async function updateStudentGrade(grade, classNum, name, bonus, value){
    student = {grade: grade, class: classNum, name: name, column: bonus, value: value}
    const response  = await fetch('/update', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(student),
    });
    data = await response.json();
    console.log(data['status']);
}

/**
 * Returns a dictionary of the metadata. Contains:
 * grades_data: A dictionary of grades. The key is the grade and the value is a list of classes.
 * tests: A list of test names.
 * 
 * Returns null on error.
 */
async function get_data(){
    // Prepare the request
    const response  = await fetch('/data', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    });

    // Send request
    data = await response.json();
    
    // Check for errors
    if (data['status'] == 'error')
        return null;

    // We don't want to return the status; It's not needed.
    return {
        grades: data['grades'],
        tests: data['tests'],
        bonus: data['bonusses'],
    };
}

function searchList(grades) {
    translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    sl = []
    for(grade in grades){
        for(classNum in grades[grade]){
            for(student in grades[grade][classNum]){
                sl.push(`${translate[grade]}${classNum} ${grades[grade][classNum][student][0]}`)
            }
        }
    }
    return sl;
}

function table_list(grades, tests, bonusses){
    translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    tl = []
    for(grade in grades){
        for(classNum in grades[grade]){
            for(student in grades[grade][classNum]){
                student_d = {}
                student_d['grade'] = translate[grade];
                student_d['class'] = classNum;
                student_d['name'] = grades[grade][classNum][student][0];
                let i = 1;
                for(test in tests){
                    student_d[tests[test]] = grades[grade][classNum][student][i];
                    i++;
                }
                for(bonus in bonusses){
                    student_d[bonusses[bonus]] = grades[grade][classNum][student][i];
                    i++;
                }
                tl.push(student_d);
            }
        }
    }
    return tl;
}
function reverseTranslate(student){
    translate = {'ט': 'nine', 'י': 'ten', 'יא': 'eleven', 'יב': 'twelve'}
    //grade and class are in the same string and are first and then the name
    grade_and_class = student.split(' ')[0];
    studentName = student.split(' ').slice(1).join(' ');
    classNum = grade_and_class.substring(grade_and_class.length - 1);
    grade = translate[grade_and_class.substring(0, grade_and_class.length - 1)];
    return [grade, classNum, studentName];
}


function generateTableHead(table, data) {
    let thead = table.createTHead();
    let row = thead.insertRow();
    for (let key of data) {
        let th = document.createElement("th");
        let text = document.createTextNode(key);
        th.appendChild(text);
        row.appendChild(th);
    }
  }
  function generateTable(table, data) {
    for (let element of data) {
      let row = table.insertRow();
      for (key in element) {
        let cell = row.insertCell();
        let text = document.createTextNode(element[key]);
        cell.appendChild(text);
      }
    }
  }

async function reloadTable(){
    console.log('reloading');
    const data = await get_data();
    const grades = data.grades;
    const tests = data.tests;
    const bonus = data.bonus;
    let students = table_list(grades, tests, bonus);
    let table = document.querySelector("table");
    let table_keys = Object.keys(students[0]);
    table.innerHTML = '';
    generateTableHead(table, table_keys);
    generateTable(table, students);
}

$('#relode').click(reloadTable);

window.onload = async () => {
    reloadTable();
}