function ajaxPost(coordinatesArray,targetArea,isPolygon,roundedArea){
    const s = JSON.stringify(coordinatesArray);
    console.log(s);
    console.log("Type of request to Python server is ", typeof s);
    console.log("JSON Stringified input:", s);
    targetArea.innerHTML = `<p>Calculating...</p>`;
    $.ajax({
        url: "/calculate",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(s),
        success: function (response) {
          console.log("Type of response from server is: ", typeof response);
          console.log("Response from the server", response); // Log the response from the server
          // const data = response
          // Parse the response string to a JSON object
          console.log(response); // Log the parsed JSON object
          /// Inside the AJAX success callback
  
          const table = document.createElement("table");
  
          // Create header row
          const headerRow = document.createElement("tr");
          const header1 = document.createElement("th");
          header1.innerText = "Key";
          const header2 = document.createElement("th");
          header2.innerText = "Sub Key";
          const header3 = document.createElement("th");
          header3.innerText = "Value";
          headerRow.appendChild(header1);
          headerRow.appendChild(header2);
          headerRow.appendChild(header3);
          table.appendChild(headerRow);
  
          // Create rows for each key-value pair in the response object
          for (const [key, value] of Object.entries(response)) {
            const row = document.createElement("tr");
            const cell1 = document.createElement("td");
            cell1.classList.add("keycell");
            cell1.innerText = key;
            const cell2 = document.createElement("td");
            const cell3 = document.createElement("td");
            if (typeof value === "object") {
              // If the value is an object, create a sub-table
              const subTable1 = document.createElement("table");
              const subTable2 = document.createElement("table");
              for (const [subKey, subValue] of Object.entries(value)) {
                let subRow1 = document.createElement("tr");
                let subRow2 = document.createElement("tr");
                let subCell1 = document.createElement("td");
                subCell1.innerText = subKey;
                let subCell2 = document.createElement("td");
                subCell2.innerText = subValue;
                subRow1.appendChild(subCell1);
                subRow2.appendChild(subCell2);
                subTable1.appendChild(subRow1);
                console.log("subtable 1",subTable1)
                subTable2.appendChild(subRow2);
                console.log("subtable 2",subTable2)
              }
              cell2.appendChild(subTable1);
              console.log("cell2",cell2)
              cell3.appendChild(subTable2);
              console.log("cell3",cell3)
            } else {
              // If the value is not an object, just display it in a cell
              cell2.innerText = value;
            }
            row.appendChild(cell1);
            row.appendChild(cell2);
            row.appendChild(cell3);
            table.appendChild(row);
          }
          if(isPolygon) {
            const row  = document.createElement('tr');
            const areaKeyCell = document.createElement("td");
            const areaValueCell = document.createElement("td");
            const areadummyValueCell = document.createElement("td");
            areaKeyCell.innerText = 'Area';
            areaValueCell.innerText = `${roundedArea} sq. m`;
            areadummyValueCell.innerText='Area';
            row.appendChild(areaKeyCell);
            row.appendChild(areadummyValueCell);
            row.appendChild(areaValueCell);
            table.appendChild(row);
          }
          // Replace the contents of the ans div with the table
          targetArea.innerHTML = "";
          targetArea.appendChild(table);
        },
  
        error: function (xhr, status, error) {
          console.log(error); // Log any errors
          console.log("gg error");
          targetArea.innerHTML = `<p>The selected area is very large for computation, please check the coordinates and try again</p>`;
        },
      });
}
