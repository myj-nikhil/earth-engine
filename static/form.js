let map;
let flag =0;
let coordinates = [];
let polygonArea;
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
    flag=1;
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
    polygonArea = spherical.computeArea(path);
    polygonArea = Math.round(polygonArea,2) + " sq. m"
    console.log(polygonArea)
    // alert(`Polygon area = ${polygonArea}`);
  });
  // console.log("out of scope", coordinates);s
  
}

initMap();




// create a polygon on the map


// show the confirmation screen
function showConfirmation() {
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;

  // validate the name and phone number
  if (name && phone && flag) {
    // show the confirmation screen and populate the user's information
    document.getElementById('name-confirmation').innerText = name;
    document.getElementById('phone-confirmation').innerText = phone;
    document.getElementById('polygon-confirmation').innerText = JSON.stringify(coordinates);
    document.getElementById('confirmation').style.display = 'block';
  } else {
    alert('Please enter all the required fields and draw an area');
  }
}

// submit the data to the server
function submitData() {
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;

  // console.log(area);
  const userData = {
    name: name,
    phone: phone,
    geojson: {
      "type": "Feature",
      "properties": {
        "name": name,
        "phone": phone,
        "area": polygonArea
      },
      "geometry": {
        "coordinates": [coordinates],
        "type": "Polygon"
      }
    }
  };

  console.log(userData); // the complete data object




  // submit the data to the server
  // ...
  // send a POST request to the API endpoint
  fetch('https://node-api-postgres-qw2rp233lq-ue.a.run.app/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  })
    .then(response => {
      if (response.ok) {
        console.log('User data submitted successfully!');
        // reset the form and map
        document.getElementById('name').value = '';
        document.getElementById('phone').value = '';
        // map.setMap(null);
        // polygon.setPath([]);
        document.getElementById('confirmation').style.display = 'none';
        alert('Data submitted successfully!');
      } else {
        alert('Error submitting user data:' + response.statusText);
      }
    })
    .catch(error => {
      console.log('Error submitting user data:', error);
    });
}