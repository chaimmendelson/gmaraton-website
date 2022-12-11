//format should be: {'grade': 'nine', 'class': 1, 'name': 'chaim', 'column': 'test1', 'value': 100}
async function updateStudentGrade(grade, classNum, name, column, value){
    student = {grade: grade, class: classNum, name: name, column: column, value: value}
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
        bonusses: data['bonusses'],
    };
}

function searchList(grades) {
    translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'}
    sl = []
    for(grade in grades){
        for(classNum in grades[grade]){
            for(student in grades[grade][classNum]){
                s = `${translate[grade]}${classNum} ${grades[grade][classNum][student]}`
                sl.push(s)
            }
        }
    }
    return sl;
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

$('#test-submit-btn').click((e) => {
    e.preventDefault(); // Do not reload
    const form = $('#test-form')[0];
    if (!form.checkValidity()) {// Validate form
        form.reportValidity();
        return;
    }
    
    // Get the values
    const student = $('#students-test-dd').val();
    const test = $('#tests-dd').val();
    const score = $('#test-score-input').val();
    student_data = reverseTranslate(student);
    const grade = student_data[0];
    const classNum = student_data[1];
    const studentName = student_data[2];
    // Update the student's grade
    updateStudentGrade(grade, classNum, studentName, test, score);
    // clear students dropdown choice
    $('#students-test-dd').val(null).trigger('change');
    // Reset score-input
    $('#test-score-input').val('');
});


$('#bonus-submit-btn').click((e) => {
    e.preventDefault(); // Do not reload
    const form = $('#bonus-form')[0];
    if (!form.checkValidity()) {// Validate form
        form.reportValidity();
        return;
    }
    
    // Get the values
    const student = $('#students-bonus-dd').val();
    const test = $('#bonus-dd').val();
    const score = $('#bonus-score-input').val();
    student_data = reverseTranslate(student);
    const grade = student_data[0];
    const classNum = student_data[1];
    const studentName = student_data[2];
    // Update the student's grade
    updateStudentGrade(grade, classNum, studentName, test, score);
    // clear students dropdown choice
    $('#students-bonus-dd').val(null).trigger('change');
    // Reset score-input
    $('#bonus-score-input').val('');
});


$('#daily-test-btn').click((e) => {
    e.preventDefault(); // Do not reload
    $('#daily-bonus').hide();
    $('#daily-test').show();
});

$('#daily-bonus-btn').click((e) => {
    e.preventDefault(); // Do not reload
    $('#daily-test').hide();
    $('#daily-bonus').show();
});


window.onload = async () => {
    const data = await get_data();
    const grades = data.grades;
    const tests = data.tests;
    const bonusses = data.bonusses;
    console.log(data);

    // Tests dropdown
    setupDropdown('tests-dd');
    fillDropdown('tests-dd', tests, false, 'select test', test => {
        console.log(`Selected test ${test}`);
    });
    
    setupDropdown('students-test-dd');
    fillDropdown('students-test-dd', searchList(grades), true, 'select name', (student) => {
        console.log(`Selected student ${student}`);
        
        // Reset score-input
        $('#test-score-input').val('');
    });
    setupDropdown('bonus-dd');
    fillDropdown('bonus-dd', bonusses, false, 'select bonus', bonus => {
        console.log(`Selected bonus ${bonus}`);
    });
    
    setupDropdown('students-bonus-dd');
    fillDropdown('students-bonus-dd', searchList(grades), true, 'select name', (student) => {
        console.log(`Selected student ${student}`);
        
        // Reset score-input
        $('#bonus-score-input').val('');
    });

    // Hide daily bonus
    $('#daily-bonus').hide();}