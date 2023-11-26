// result.js
async function fetchNeo4jData() {
    // Retrieve the search criteria from storage
    const urlParams = new URLSearchParams(window.location.search);
    const searchData = {
        id: urlParams.get('id'),
        bodypart: urlParams.get('bodypart'),
        disease: urlParams.get('disease'),
        symptom: urlParams.get('symptom')
    };

    if (!searchData) {
        console.error('No search data found');
        return;
    }

    // Make the API call with the retrieved search data
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

    return await response.json();
}


function displayResults(data) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = ''; // Clear previous results

    // Log the data sent to the backend
    console.log('Data sent to backend:', data);
    // Assuming 'data' is an array of result objects
    data.forEach(result => {
        const listItem = document.createElement('li');
        listItem.textContent = `ID: ${result.id}, Labels: ${result.labels.join(', ')}, Properties: ${JSON.stringify(result.properties)}`;
        resultsList.appendChild(listItem);
    });
}

// Fetch and display the results when the page loads
document.addEventListener("DOMContentLoaded", async function () {
    try {
        const data = await fetchNeo4jData();
        if (data && data.length > 0) {
            displayResults(data);
        } else {
            // Handle the case where no data is returned
            document.getElementById('resultsList').innerHTML = '<li>No results found</li>';
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
