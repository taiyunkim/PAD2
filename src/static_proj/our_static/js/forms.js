// $(document).ready(function() {
//   var comp = document.getElementById("id_comparison");
//
//   if (comp.value == "PAD") {
//    $("#div_id_cut_off").show();
//    $("div_id_separation_1").hide();
//    $("div_id_separation_2").hide();
//   } else if (comp.value == "States") {
//    $("#div_id_cut_off").hide();
//    $("div_id_separation_1").show();
//    $("div_id_separation_2").show();
//   }
//
// });


$("#div_id_separation_1").hide();
$("#div_id_separation_2").hide();

fillOptions = function() {
  var comparison = document.getElementById('id_comparison').value;

  if (comparison == "PAD") {
     $("#div_id_cut_off").show();
     $("#div_id_separation_1").hide();
     $("#div_id_separation_2").hide();
   } else if (comparison == "States") {
     $("#div_id_cut_off").hide();
     $("#div_id_separation_1").show();
     $("#div_id_separation_2").show();
    }

  // $('#id_selected_peaks').text(filename);
};

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip({
      placement : 'top'
  });
});
