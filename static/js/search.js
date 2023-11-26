function searchNeo4j() {
    var name = document.getElementById('name').value;
    var id = document.getElementById('id').value;
    var disease = document.getElementById('disease').value;
    var bodypart = document.getElementById('bodyPart').value;
    var symptoms = $('#symptoms').val(); // Since this is a Select2 multiselect, use jQuery to get the selected values

    // Store search data in sessionStorage or localStorage
    sessionStorage.setItem('searchData', JSON.stringify({
        name: name,
        id: id,
        bodypart: bodypart,
        disease: disease,
        symptom: symptoms.join(', ') // Assuming your backend expects a string of symptoms
    }));

    // Create a POST request to send this data to your Flask backend
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            id: id,
            bodypart: bodypart,
            disease: disease,
            symptom: symptoms.join(', ') // Assuming your backend expects a string of symptoms
        })
    })
    .then(response => response.json())
    .then(data => {
        const params = new URLSearchParams({
            name: name,
            id: id,
            bodypart: bodypart,
            disease: disease,
            symptom: symptoms.join(', ') // Assuming your backend expects a string of symptoms
        }).toString();
        window.location.href = `result.html?${params}`; // Redirect to result.html with search parameters
    })
        // Redirect to results page or handle displaying results
    
    .catch(error => console.error('Error:', error));
}