//format should be: {'grade': 'nine', 'class': 1, 'name': 'chaim', 'column': 'test1', 'value': 100}
async function update(grade, classNum, column, value){
    data = {grade: grade, class: classNum, column: column, value: value}
    const response  = await fetch('/admin_update', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
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
        bonusses: data['bonusses'],
        competition : data['competition'],
        attendence : data['attendence'],
        additional : data['additional'],
    };
}

function searchList(grades) {
    translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    sl = []
    for(grade in grades){
        for(classNum in grades[grade]){
            sl.push(`${translate[grade]}${classNum}`)
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

function attendents_table_list(additional, attetdents){
    let translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    //format = {"nine": {"competition": 0, "1": {"attend1": 0, "attend2": 0, "attend3": 0}}}
    tl = []
    for(grade in additional){
        for(classNum in additional[grade]){
            if (classNum == 'competition')
                continue;
            at = {}
            at['grade'] = translate[grade];
            at['class'] = classNum;
            for(attetdent in attetdents){
                let att = attetdents[attetdent];
                at[att] = additional[grade][classNum][att];
            }
            tl.push(at);
        }
    }
    return tl;
}


function competition_table_list(additional, competition){
    let translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    //format = {"nine": {"competition": 0, "1": {"attend1": 0, "attend2": 0, "attend3": 0}}}
    tl = []
    for(grade in additional){
        at = {}
        at['grade'] = translate[grade];
        at['score'] = additional[grade]['competition'];
        tl.push(at);
        }
    return tl;
}

function reverseTranslate(grade_and_class){
    translate = {'ט': 'nine', 'י': 'ten', 'יא': 'eleven', 'יב': 'twelve'}
    //grade and class are in the same string and are first and then the name
    classNum = grade_and_class.substring(grade_and_class.length - 1);
    grade = translate[grade_and_class.substring(0, grade_and_class.length - 1)];
    return [grade, classNum];
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
    const bonus = data.bonusses;
    let students = table_list(grades, tests, bonus);
    let table = document.querySelector("table");
    let table_keys = Object.keys(students[0]);
    table.innerHTML = '';
    generateTableHead(table, table_keys);
    generateTable(table, students);

    //setup attendents table
    let attendents = data.attendence;
    let additional = data.additional;
    let competition = data.competition;
    let attendents_table = document.querySelector("#attendents_table");
    attendents = attendents_table_list(additional, attendents);
    let attendents_keys = Object.keys(attendents[0]);
    attendents_table.innerHTML = '';
    generateTableHead(attendents_table, attendents_keys);
    generateTable(attendents_table, attendents);

    //setup competition table
    let competition_table = document.querySelector("#competition-table");
    competition = competition_table_list(additional, competition);
    let competition_keys = Object.keys(competition[0]);
    competition_table.innerHTML = '';
    generateTableHead(competition_table, competition_keys);
    generateTable(competition_table, competition);
};

$('#reload').click(reloadTable);

function setupDropdown(dropdownID) {
    // Get the dropdown
    const dropdown = $(`#${dropdownID}`);

    // We need one empty option in order to show the placeholder
    dropdown.append('<option>');

    // Make it a select2 dropdown
    dropdown.select2({placeholder: 'No option selected'});
}

function fillDropdown(dropdownID, data, showSearch, placeholder, onselect) {
    // Get the dropdown
    const dropdown = $(`#${dropdownID}`);
    
    // Clear leftovers
    clearDropdown(dropdownID)

    // Fill the dropdown
    dropdown.select2({
        data: data,
        minimumResultsForSearch: (showSearch ? 0 : -1),
        placeholder: placeholder,
        allowClear: true
    });

    // onselect
    dropdown.on('select2:select', (e) => {
        onselect(e.params.data.id);
    });

    // Auto focus on search field when dropdown is opened
    if (showSearch) {
        dropdown.on('select2:open', () => {
            document.querySelector('.select2-search__field').focus();
        });
    }
};

function clearDropdown(dropdownID) {
    // Get the dropdown
    const dropdown = $(`#${dropdownID}`);

    // Clear the dropdown, and re-add the empty option to show placeholder
    dropdown.empty();
    dropdown.append('<option>');
}

$('#submit-daily-btn').click((e) => {
    e.preventDefault(); // Do not reload
    const form = $('#daily-form')[0];
    if (!form.checkValidity()) {// Validate form
        form.reportValidity();
        return;
    }
    
    // Get the values
    const grade_and_class = $('#daily-classes').val();
    const attendence = $('#daily-key').val();
    const score = $('#daily-value-input').val();
    data = reverseTranslate(grade_and_class);
    const grade = data[0];
    const classNum = data[1];
    // Update the student's grade
    update(grade, classNum, attendence, score);
    // clear students dropdown choice
    $('#daily-classes').val(null).trigger('change');
    // Reset score-input
    $('#daily-value-input').val('');
});


$('#submit-comp-btn').click((e) => {
    e.preventDefault(); // Do not reload
    const form = $('#comp-form')[0];
    if (!form.checkValidity()) {// Validate form
        form.reportValidity();
        return;
    }
    
    // Get the values
    let translate = {'ט': 'nine', 'י': 'ten', 'יא': 'eleven', 'יב': 'twelve'}
    const grade = translate[$('#comp-grade').val()];
    const score = $('#comp-value-input').val();
    // Update the student's grade
    update(grade, 0, 'competition', score);
    // clear students dropdown choice
    $('#comp-grade').val(null).trigger('change');
    // Reset score-input
    $('#comp-value-input').val('');
});


$('#daily-btn').click((e) => {
    e.preventDefault(); // Do not reload
    $('#comp-data').hide();
    $('#daily-data').show();
});

$('#comp-btn').click((e) => {
    e.preventDefault(); // Do not reload
    $('#daily-data').hide();
    $('#comp-data').show();
});


window.onload = async () => {
    reloadTable();
    translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    const data = await get_data();
    const grades = data.grades;
    const attendence = data.attendence;
    let comp_grades = [];
    let grades_list = Object.keys(grades);
    for (let grade in grades_list) {
        comp_grades.push(translate[grades_list[grade]]);
    }

    // Tests dropdown
    setupDropdown('daily-key');
    fillDropdown('daily-key', attendence, false, 'select day', day => {
        console.log(`Selected day ${day}`);
    });
    
    setupDropdown('daily-classse');
    fillDropdown('daily-classes', searchList(grades), true, 'select class', classNum => {
        console.log(`Selected class ${classNum}`);
        
        // Reset score-input
        $('#daily-value-input').val('');
    });
    
    setupDropdown('comp-grade');
    fillDropdown('comp-grade', comp_grades, false, 'select grade', grade => {
        console.log(`Selected ${grade}`);
        
        // Reset score-input
        $('#comp-value-input').val('');
    });

    // Hide daily bonus
    $('#comp-data').hide();}