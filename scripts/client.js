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
    };
}

function setupDropdown(dropdownID) {
    // Get the dropdown
    const dropdown = $(`#${dropdownID}`);

    // We need one empty option in order to show the placeholder
    dropdown.append('<option>');

    // Make it a select2 dropdown
    dropdown.select2({placeholder: 'No option selected'});
}

function fillDropdown(dropdownID, data, showSearch, onselect) {
    // Get the dropdown
    const dropdown = $(`#${dropdownID}`);
    
    // Clear leftovers
    clearDropdown(dropdownID)

    // Fill the dropdown
    dropdown.select2({
        data: data,
        minimumResultsForSearch: (showSearch ? 0 : -1),
        placeholder: 'Select an option',
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
    const dropdown = $('#${dropdownID}');

    // Clear the dropdown, and re-add the empty option to show placeholder
    dropdown.empty();
    dropdown.append('<option>');
}

window.onload = async () => {
    const data = await get_data();
    const grades = data.grades;
    console.log(data);

    setupDropdown('grades-dd');
    setupDropdown('classes-dd');
    setupDropdown('students-dd');

    fillDropdown('grades-dd', Object.keys(grades), false, (grade) => {
        clearDropdown('students-dd') // Clear leftovers
        fillDropdown('classes-dd', Object.keys(grades[grade]), true, (classNum) => {
            fillDropdown('students-dd', grades[grade][classNum], true, (student) => {
                console.log(student);
            });
        });
    });
};