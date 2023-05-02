 // get the form element

 // add an event listener to the form for when it is submitted
 document.getElementById("submit").addEventListener("click", () => {
   // prevent the default form submission behavior
   

   // get the values of the form inputs
   const topLeftLat = parseFloat(
     document.getElementById("top-left-lat").value
   );
   const topLeftLong = parseFloat(
     document.getElementById("top-left-long").value
   );
   const bottomRightLat = parseFloat(
     document.getElementById("bottom-right-lat").value
   );
   const bottomRightLong = parseFloat(
     document.getElementById("bottom-right-long").value
   );

   // validate the input values
   if (
     isNaN(topLeftLat) ||
     isNaN(topLeftLong) ||
     isNaN(bottomRightLat) ||
     isNaN(bottomRightLong)
   ) {
     alert("Please enter valid coordinates.");
     return;
   }

   // calculate the other two corner coordinates
   const topRightLat = topLeftLat;
   const topRightLong = bottomRightLong;
   const bottomLeftLat = bottomRightLat;
   const bottomLeftLong = topLeftLong;

   // create an array of the corner coordinates in clockwise order
   const coordinates = [
     [topLeftLong, topLeftLat],
     [topRightLong, topRightLat],
     [bottomRightLong, bottomRightLat],
     [bottomLeftLong, bottomLeftLat],
     [topLeftLong, topLeftLat],
   ];
   targetArea = document.getElementById("ans");
   let turfPolygon = turf.polygon([coordinates]);
   let area = turf.area(turfPolygon);
   console.log(`Area of the polygon is ${area}`)
   const roundedArea = Math.round(area * 100) / 100;
  ajaxPost(coordinates,targetArea,true,roundedArea);
 });

//  document.getElementById("submit2").addEventListener("click", () => {
//   // prevent the default form submission behavior
  

//   // get the values of the form inputs
//   const topLeftLat = parseFloat(
//     document.getElementById("top-left-lat").value
//   );
//   const topLeftLong = parseFloat(
//     document.getElementById("top-left-long").value
//   );
//   const bottomRightLat = parseFloat(
//     document.getElementById("bottom-right-lat").value
//   );
//   const bottomRightLong = parseFloat(
//     document.getElementById("bottom-right-long").value
//   );

//   // validate the input values
//   if (
//     isNaN(topLeftLat) ||
//     isNaN(topLeftLong) ||
//     isNaN(bottomRightLat) ||
//     isNaN(bottomRightLong)
//   ) {
//     alert("Please enter valid coordinates.");
//     return;
//   }

//   // calculate the other two corner coordinates
//   const topRightLat = topLeftLat;
//   const topRightLong = bottomRightLong;
//   const bottomLeftLat = bottomRightLat;
//   const bottomLeftLong = topLeftLong;

//   // create an array of the corner coordinates in clockwise order
//   const coordinates = [
//     [topLeftLong, topLeftLat],
//     [topRightLong, topRightLat],
//     [bottomRightLong, bottomRightLat],
//     [bottomLeftLong, bottomLeftLat],
//     [topLeftLong, topLeftLat],
//   ];
//   targetArea = document.getElementById("ans");
//   let turfPolygon = turf.polygon([coordinates]);
//   let area = turf.area(turfPolygon);
//   console.log(`Area of the polygon is ${area}`)
//   const roundedArea = Math.round(area * 100) / 100;
//  secondajaxPost(coordinates,targetArea,true,roundedArea);
// });