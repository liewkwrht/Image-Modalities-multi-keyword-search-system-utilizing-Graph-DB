function searchNeo4j() {
    // Get values from form fields
    var name = document.getElementById('name').value;
    var id = document.getElementById('id').value;
    var disease = document.getElementById('disease').value;
    var bodypart = document.getElementById('body_part').value;
    var symptoms = $('#symptoms').val(); // Since this is a Select2 multiselect, use jQuery to get the selected values

    // Convert symptoms array to a string if not null or undefined
    var symptomsString = symptoms ? symptoms.join(', ') : '';

    // Store search data in sessionStorage for later use on the results page
    sessionStorage.setItem('searchData', JSON.stringify({
        name: name,
        id: id,
        bodypart: bodypart,
        disease: disease,
        symptom: symptomsString // Join the symptoms array into a string
    }));

    // Create a POST request to send this data to your Flask backend
    async function searchNeo4j() {
        // Get values from form fields
        var name = document.getElementById('name').value;
        var id = document.getElementById('id').value;
        var disease = document.getElementById('disease').value;
        // Ensure this key matches the backend expectation
        var bodyPart = document.getElementById('bodyPart').value;
        var symptoms = $('#symptoms').val().join(', '); // Convert array to a comma-separated string if not null or undefined
        
        // Object to send in the POST request
        const postData = {
            name: name,
            id: id,
            body_part: bodyPart,  // Updated key to match the backend
            disease: disease,
            symptom: symptoms
        };
        
    
        // Make the API call
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(postData)
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Process the data
            if (data && data.length > 0) {
                // Store search data and redirect if needed
            } else {
                console.log('No results found');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
    
    // Event listener for form submission
    document.getElementById('searchForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        searchNeo4j();
    });
    
document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    searchNeo4j();
}); 
}