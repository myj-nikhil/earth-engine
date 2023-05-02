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
    const roundedArea = Math.round(area * 100) / 100;
    ajaxPost(coordinates,targetArea,true,roundedArea);
}
else {
    targetArea.innerHTML = 'Please select atleast 3 points'
}

}

// function mySecondfunction() {
//   console.log("button clicked")
//   const targetArea = document.getElementById("ans");
//   if (coordinates.length > 3) {
//     console.log(coordinates)
//     const s = JSON.stringify(coordinates);
//     let turfPolygon = turf.polygon([coordinates]);
//     let area = turf.area(turfPolygon);
//     console.log(`Area of the polygon is ${area}`)
//     const roundedArea = Math.round(area * 100) / 100;
//     secondajaxPost(coordinates,targetArea,true,roundedArea);
// }
// else {
//     targetArea.innerHTML = 'Please select atleast 3 points'
// }

// }
