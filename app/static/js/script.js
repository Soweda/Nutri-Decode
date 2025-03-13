// Store global nutrients data for later use
let globalNutrients = {};

// Handle image preview when a file is selected
document.getElementById("fileInput").addEventListener("change", function (event) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("imagePreview").innerHTML = `<img src="${e.target.result}" alt="Selected Image" style="max-width: 100%; height: auto;">`;
        };
        reader.readAsDataURL(file);
    }
});

// Handle file upload
document.getElementById("uploadButton").addEventListener("click", function () {
    let fileInput = document.getElementById("fileInput");

    if (!fileInput.files.length) {
        alert("Please select a file before uploading.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("File uploaded successfully!");
            document.getElementById("extractedText").innerText = data.extracted_text;

            // Store the nutrient data globally and update the table
            globalNutrients = data.nutrients;
            updateNutrientValues(100); // Default to 100g initially

            document.getElementById("imagePreview").innerHTML = `<img src="${data.uploaded_url}" alt="Uploaded Image" style="max-width: 100%; height: auto;">`;
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
});

// Function to update nutrient values in the table based on selected weight
function updateNutrientValues(weight) {
    console.log("Updating nutrients for weight:", weight, "with data:", globalNutrients);
    document.getElementById("progressValue").textContent = `${weight}g`;
    let nutrientTable = document.getElementById("nutrientBody");
    nutrientTable.innerHTML = ""; // Clear previous data

    if (Object.keys(globalNutrients).length === 0) {
        nutrientTable.innerHTML = "<tr><td colspan='2'>No nutritional data found</td></tr>";
        return;
    }

    let fragment = document.createDocumentFragment();
    for (const [nutrient, value] of Object.entries(globalNutrients)) {
        let adjustedValue = ((parseFloat(value) * weight) / 100).toFixed(2); // Correct scaling
        let row = document.createElement("tr");
        row.innerHTML = `<td>${nutrient}</td><td>${adjustedValue}g</td>`;
        fragment.appendChild(row);
    }
    nutrientTable.appendChild(fragment);
}

// Event listener for the scroll bar
document.getElementById("progressBar").addEventListener("input", function () {
    let selectedWeight = this.value;
    updateNutrientValues(selectedWeight); // Update nutrient values based on user selection
});
