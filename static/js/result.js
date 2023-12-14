async function fetchAndDisplayResults() {
    const searchData = JSON.parse(sessionStorage.getItem('searchData'));

    try {
        // Call the API with the search data
        const response = await fetch('/api/search', {
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
    const resultsContainer = document.getElementById('resultsContainer');

    // Check if data has content
    if (data && data.data) {
        resultsContainer.innerHTML = ''; // Clear previous results

        // Assuming 'data' is an object with 'data' property containing results
        const resultData = data.data;

        for (const label in resultData) {
            const labelContainer = document.createElement('div');
            labelContainer.innerHTML = `<h3>${label} (${resultData[label].count} results)</h3>`;

            const nodesList = document.createElement('ul');
            const nodes = resultData[label].nodes;

            nodes.forEach(node => {
                const listItem = document.createElement('li');
                listItem.textContent = JSON.stringify(node.properties);
                nodesList.appendChild(listItem);
            });

            labelContainer.appendChild(nodesList);
            resultsContainer.appendChild(labelContainer);
        }
    } else {
        resultsContainer.innerHTML = '<p>No results found</p>';
    }
}

// Call fetchAndDisplayResults when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fetchAndDisplayResults);
