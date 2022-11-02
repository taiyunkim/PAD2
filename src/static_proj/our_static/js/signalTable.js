// javascript for signal selection from database table



// when save button is clicked, display the files selected in forms.
saveSelect = function(){
    sTable = $('#table').DataTable()
    var rowArray = sTable.rows('.selected')
	
	
    // var rowArray = $('.selected');
    // alert(rowArray[0].id)
    var filename = '';
    for (var i = 0; i < rowArray.count(); i++) {
        filename = filename.concat(rowArray.data()[i][0]);
        filename = filename.concat('\n');
    }
    $('#id_selected_field').text(filename);

};
