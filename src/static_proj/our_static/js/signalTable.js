// javascript for signal selection from database table



// when save button is clicked, display the files selected in forms.
saveSelect = function(){
    sTable = $('#table').DataTable()
    var rowArray = sTable.rows('.selected')
	
    var select = document.getElementById('id_interest');


	var filename = '';
    for (var i = 0; i < rowArray.count(); i++) {
        filename = filename.concat(rowArray.data()[i][0]);
        filename = filename.concat('\n');

        var name = rowArray.data()[i][0];
        var fileId = rowArray.data()[i][1];
        var el = document.createElement("option");
        el.textContent = name;
        el.value = fileId;
        select.appendChild(el)

    }
    $('#id_selected_field').text(filename);

};
