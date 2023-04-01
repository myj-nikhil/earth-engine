mapboxgl.accessToken = 'pk.eyJ1IjoieW9nZXNoLW0iLCJhIjoiY2xmcDM4Z3IwMTI4MjNwcms5aWhyNHU0ZSJ9.tOKeQV2nbOs6JQBMpCTU0g';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [78.07, 22.89],// starting position [lng, lat]
    zoom: 4 // starting zoom 
});

const draw = new MapboxDraw({
    displayControlsDefault: false,
    // Select which mapbox-gl-draw control buttons to add to the map.
    controls: {
        polygon: true,
        trash: true
    },
    // Set mapbox-gl-draw to draw by default.
    // The user does not have to click the polygon control button first.
    defaultMode: 'draw_polygon'
});
map.addControl(new mapboxgl.NavigationControl());
map.addControl(draw);
map.addControl(
    new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    mapboxgl: mapboxgl
    })
    );


function myfunction() {
    console.log("button clicked")
    const data = draw.getAll();
    console.log("length of features", data.features.length)
    const targetArea = document.getElementById("ans");
    if (data.features.length > 0) {
        const pointArray = data.features[0].geometry.coordinates[0];
        console.log(pointArray)
        console.log(pointArray.length)
        if (pointArray.length > 2) {
            console.log(pointArray)
            const s = JSON.stringify(pointArray);
            const area = turf.area(data);
            const rounded_area = Math.round(area * 100) / 100;
            console.log("Type of request to Python server is ", typeof s)
            console.log("JSON Stringified input:", s);
            targetArea.innerHTML = `<p>Calculating...</p>`
            $.ajax({
                url: "/calculate",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify(s),
                success: function (response) {
                    console.log("Type of response from server is: ", typeof response)
                    console.log("Response from the server", response); // Log the response from the server
                    // const data = response 
                    // Parse the response string to a JSON object
                    console.log(response); // Log the parsed JSON object
                    /// Inside the AJAX success callback

                    const table = document.createElement('table');

                    // Create header row
                    const headerRow = document.createElement('tr');
                    const header1 = document.createElement('th');
                    header1.innerText = 'Key';
                    const header2 = document.createElement('th');
                    header2.innerText = 'Value';
                    headerRow.appendChild(header1);
                    headerRow.appendChild(header2);
                    table.appendChild(headerRow);

                    // Create rows for each key-value pair in the response object
                    for (const [key, value] of Object.entries(response)) {
                        const row = document.createElement('tr');
                        const cell1 = document.createElement('td');
                        cell1.innerText = key;
                        const cell2 = document.createElement('td');
                        if (typeof value === 'object') {
                            // If the value is an object, create a sub-table
                            const subTable = document.createElement('table');
                            for (const [subKey, subValue] of Object.entries(value)) {
                                const subRow = document.createElement('tr');
                                const subCell1 = document.createElement('td');
                                subCell1.innerText = subKey;
                                const subCell2 = document.createElement('td');
                                subCell2.innerText = subValue;
                                subRow.appendChild(subCell1);
                                subRow.appendChild(subCell2);
                                subTable.appendChild(subRow);
                            }
                            cell2.appendChild(subTable);
                        } else {
                            // If the value is not an object, just display it in a cell
                            cell2.innerText = value;
                        }
                        row.appendChild(cell1);
                        row.appendChild(cell2);
                        table.appendChild(row);
                    }
                    const row  = document.createElement('tr');
                    const areaKeyCell  = document.createElement('td');
                    const areaValueCell = document.createElement('td');
                    areaKeyCell.innerText = 'Area (sq m.)'
                    areaValueCell.innerText = rounded_area
                    row.appendChild(areaKeyCell)
                    row.appendChild(areaValueCell)
                    table.appendChild(row) 
                    // Replace the contents of the ans div with the table
                    const targetArea = document.getElementById("ans");
                    targetArea.innerHTML = '';
                    targetArea.appendChild(table);

                },

                error: function (xhr, status, error) {
                    console.log(error); // Log any errors
                    const targetArea = document.getElementById("ans");
                    targetArea.innerHTML = `<p>Please select a smaller area</p>`

                }
            });
        }
        else {
            targetArea.innerHTML = 'Please select atleast 3 points'
        }
    }
    else {
        console.log("feature length", data.features.length)
        targetArea.innerHTML = 'Please select atleast 3 points'
    }
}