/**
 * Gets the result from the server
 * @returns Null on error, otherwise the results
 */
const get_results = async () => {
    const response = await fetch('/results', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    });
    data = await response.json();
    if (data['status'] == 'error')
        return null;
    
    return data['results'];
};

const getClassName = (grade, classNum) => {
    const translate = {'nine': 'ט', 'ten': 'י', 'eleven': 'יא', 'twelve': 'יב'};
    return `${translate[grade]} ${classNum}`;
}

const createChart = (labels, scores) => {
    const data = {
        labels: labels,
        datasets: [{
            label: 'Scores',
            data: scores,
            borderWidth: 1
        }]
    };

    const config = {
        type: 'bar',
        data,
        options: {
            indexAxis: 'y',
        }
      };

    new Chart(document.getElementById('chart'), config);
};

window.onload = async () => {
    const results = await get_results();
    if (results == null)
        return;

    const labels = [];
    const scores = [];
    for (const grade of Object.keys(results)) {
        for (const classNum of Object.keys(results[grade])) {
            labels.push(getClassName(grade, classNum));
            scores.push(results[grade][classNum]);
        }
    }

    createChart(labels, scores);
}