async function initMap() {
  const { Geocoder } = await google.maps.importLibrary("geocoding");
  const geocoder = new Geocoder();
  console.log("noerror");
  document.getElementById("submit").addEventListener("click", () => {
    const textArea = document.getElementById("textdiv");
    textArea.innerHTML = "";
    const coords = document.getElementById("latlng").value;
    const coordsArray = coords.split(",", 2);
    for (i = 0; i < 2; i++) {
      coordsArray[i] = parseFloat(coordsArray[i]);
    }
    geocodeLatLng(geocoder, coordsArray);
    reversedArray = coordsArray.reverse();
    targetArea = document.getElementById("secondans");
    ajaxPost(reversedArray,targetArea,false);
  });

  function geocodeLatLng(geocoder, coordsArray) {
    const latlng = {
      lat: coordsArray[0],
      lng: coordsArray[1],
    };

    geocoder
      .geocode({ location: latlng })
      .then((response) => {
        if (response.results[0]) {
          const result = response.results;
          console.log(result);
          console.log(`length is : ${result.length}`);
          console.log(response.results[0].formatted_address);
          const targetArea = document.getElementById("ans");
          targetArea.innerText = `Address: ${response.results[0].formatted_address}`;
        } else {
          window.alert("No results found");
        }
      })
      .catch((e) => window.alert("Geocoder failed due to: " + e));
  }
}

initMap();
