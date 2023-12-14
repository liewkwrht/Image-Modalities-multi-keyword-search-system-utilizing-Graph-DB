async function fetchAndDisplayResults() {
    // Retrieve the search criteria from the query string
    const urlParams = new URLSearchParams(window.location.search);

    // Parse the patient_id as an integer.
    const patientId = parseInt(urlParams.get('patient_id'), 10);

    // Construct the search data object.
    const searchData = {
        name: urlParams.get('name') || "", // If null or undefined, default to an empty string.
        patient_id: !isNaN(patientId) ? patientId : undefined, // Use the parsed patient_id if it's a valid number, otherwise undefined.
        bodypart: urlParams.get('bodypart') || "", // If null or undefined, default to an empty string.
        disease: urlParams.get('disease') || "", // If null or undefined, default to an empty string.
        symptoms: urlParams.get('symptoms') ? urlParams.get('symptoms').split(',') : [],
        targetClasses: urlParams.get('targetClasses') ? urlParams.get('targetClasses').split(',') : ["X_ray", "CT", "MRI", "DSI", "US"]
    };

    console.log('Search parameters received:', searchData);
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
        console.log('API Response:', data);
        displayResults(data);
    } catch (error) {
        console.error('Error fetching and displaying results:', error);
    }
}
function displayResults(data) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = ''; // Clear previous results

    // Check if data has content and has the 'data' property
    if (data && data.data) {
        // Loop over each modality in the data
        Object.keys(data.data).forEach(modality => {
            // Check if the current modality has 'nodes'
            if (data.data[modality].nodes) {
                // Loop over each node in the 'nodes' array
                data.data[modality].nodes.forEach(node => {
                    // Format the display string
                    const displayString = `C-GET [Study Instance UID = ${node.properties.uid}] [Modality = ${modality}]`;

                    // Create list item and append it to the results list
                    const listItem = document.createElement('li');
                    listItem.textContent = displayString;
                    resultsList.appendChild(listItem);
                });
            }
        });
    } else {
        resultsList.innerHTML = '<li>No results found</li>';
    }
}

// Call fetchAndDisplayResults when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fetchAndDisplayResults);




// Call fetchAndDisplayResults when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fetchAndDisplayResults);


// Call fetchAndDisplayResults when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', fetchAndDisplayResults);
