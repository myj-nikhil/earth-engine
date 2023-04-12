// Initialize and add the map
let map;
let coordinates = [];
async function initMap() {
  // The location of Uluru
  // const position = { lat: -25.344, lng: 131.031 };
  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  // const { AdvancedMarkerView } = await google.maps.importLibrary("marker");
  const { DrawingManager } = await google.maps.importLibrary("drawing");
  const { spherical } = await google.maps.importLibrary("geometry");
  const { SearchBox } = await google.maps.importLibrary("places");

  // The map, centered at Uluru
  map = new Map(document.getElementById("map"), {
    center: { lat: 24, lng: 80 },
    zoom: 5,
    mapTypeId: "hybrid",
  });

  map.setTilt(45);

  // The marker, positioned at Uluru
  // const marker2 = new AdvancedMarkerView({
  //   map: map,
  //   position: position,
  //   title: "Uluru",
  // });

  const input = document.getElementById("pac-input");
  const search = new SearchBox(input);

  map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

  map.addListener("bounds_changed", () => {
    search.setBounds(map.getBounds());
    console.log("bounds changed");
  });

  let markers = [];

  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  search.addListener("places_changed", () => {
    const places = search.getPlaces();
    console.log(`Places are ${places}`);
    console.log("places changed");
    if (places.length == 0) {
      return;
    }

    // Clear out the old markers.
    markers.forEach((marker) => {
      marker.setMap(null);
    });
    markers = [];

    // For each place, get the icon, name and location.
    const bounds = new google.maps.LatLngBounds();

    places.forEach((place) => {
      if (!place.geometry || !place.geometry.location) {
        console.log("Returned place contains no geometry");
        return;
      }

      const icon = {
        url: place.icon,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 34),
        scaledSize: new google.maps.Size(25, 25),
      };

      // Create a marker for each place.
      markers.push(
        new google.maps.Marker({
          map,
          icon,
          title: place.name,
          position: place.geometry.location,
        })
      );
      console.log(markers);
      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });

  const DrawManager = new DrawingManager({
    drawingMode: google.maps.drawing.OverlayType.POLYGON,
    drawingControlOptions: {
      position: google.maps.ControlPosition.RIGHT_TOP,
      drawingModes: [
        // google.maps.drawing.OverlayType.MARKER,
        google.maps.drawing.OverlayType.CIRCLE,
        google.maps.drawing.OverlayType.POLYGON,
        // google.maps.drawing.OverlayType.RECTANGLE,
      ],
    },
  });
  DrawManager.setMap(map);

  DrawManager.addListener("circlecomplete", function (circle) {
    console.log("circle drawn");
    let radius = circle.getRadius();
    console.log(`Radius = ${radius}`);
    let circleArea = spherical.computeArea(circle);
    console.log(`Circle Area = ${circleArea}`);
    let circleCenter = circle.getCenter();
    console.log(circleCenter);
    let circleCoordinates =[circleCenter.lng(),circleCenter.lat()]
    console.log(circleCoordinates);
  });

  DrawManager.addListener("polygoncomplete", function (polygon) {
    console.log("Polygon drawn");
    let path = polygon.getPath();
    console.log(path);
    // clear the stored coordinates
    coordinates =[];
    for (let i = 0; i < path.getLength(); i++) {
      let latLng = path.getAt(i);
      coordinates.push([latLng.lng(),latLng.lat() ]);
    }
    console.log(coordinates);
    coordinates = coordinates.concat([coordinates[0]]);
    console.log("Final coordinates : ",coordinates);
    // let polygonArea = spherical.computeArea(polygon);
    // alert(`Polygon area = ${polygonArea}`);
  });
  // console.log("out of scope", coordinates);
}

initMap();

function myfunction() {
  console.log("button clicked")
  const targetArea = document.getElementById("ans");
  if (coordinates.length > 3) {
    console.log(coordinates)
    const s = JSON.stringify(coordinates);
    let turfPolygon = turf.polygon([coordinates]);
    let area = turf.area(turfPolygon);
    console.log(`Area of the polygon is ${area}`)
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


  // if (coordinates.length > 0) {
  //     const coordinates = data;
  //     console.log(`Point array : ${coordinates}`)
  //     console.log(`Point array's length : ${coordinates.length}`)
  //     //old code here
  // }
  // else {
  //     console.log("feature length", data.length)
  //     targetArea.innerHTML = 'Please select atleast 3 points'
  // }
}
