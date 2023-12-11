async function fetchAndDisplayResults() {
    // Retrieve the search criteria from the query string
    const urlParams = new URLSearchParams(window.location.search);
    const searchData = {
        name: urlParams.get('name'),
        id: urlParams.get('id'),
        bodypart: urlParams.get('bodyPart'), // changed from bodyPart to bodypart
        disease: urlParams.get('disease'),
        symptoms: urlParams.get('symptoms') // changed from symptoms to symptom
    };

    try {
        // Call the API with the search data
        const response = await fetch('http://127.0.0.1:5000/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error fetching and displaying results:', error);
    }
}

function displayResults(data) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = ''; // Clear previous results

    // Check if data has content
    if (data && data.length > 0) {
        // Assuming 'data' is an array of result objects
        data.forEach(result => {
            const listItem = document.createElement('li');
            listItem.textContent = `ID: ${result.id}, Labels: ${result.labels.join(', ')}, Properties: ${JSON.stringify(result.properties)}`;
            resultsList.appendChild(listItem);
        });
    } else {
        resultsList.innerHTML = '<li>No results found</li>';
    }
}

// Call fetchAndDisplayResults when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fetchAndDisplayResults);
