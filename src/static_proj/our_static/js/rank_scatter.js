// Selected file name
var highlight_name;
if (json_data['highlight_name'] != "None") {
    highlight_name = json_data['highlight_name'];
    
}

var filename;
var cor;
var fileID;
var interest;
var category;
var interest_id;
if (json_data['cor'] != "None") {
    cor = json_data['cor'];
}
if (json_data['filename'] != "None") {
    filename = json_data['filename'];
}
if (json_data['fileID'] != "None") {
    fileID = json_data['fileID'];
}
if (json_data['interest_name'] != "None") {
    interest = json_data["interest_name"];
}
if (json_data['category'] != "None") {
    category = json_data['category'];
}
if (json_data['interest_id'] != "None") {
    interest_id = json_data['interest_id'];
}
console.log(interest_id);

var ranking = [];
for (i = 1;  i <= fileID.length; i++){
    ranking.push(i);
}

var trace1 = {
    x: ranking,
    y: cor,
    mode: 'markers',            
    type: 'scatter',
    name: category,
    text: fileID,
    marker: { size: 12 }
};
// console.log(highlight_name);
// var index = filename.indexOf(highlight_name);
// console.log(index);
// console.log(filename);

var index = [];
highlight_name.forEach(function(f){
    index.push(filename.indexOf(f));
})
index = index.filter(function(x){return x > -1});
// console.log(index);
// console.log(ranking[index]);
var trace2 = {
    // x: ranking[index],
    // y: cor[index],
    x: index.map(i => ranking[i]),
    y: index.map(i => cor[i]),
    mode: 'markers',            
    type: 'scatter',
    name: 'Other selected signals',
    // text: fileID[index],
    text: index.map(i => fileID[i]),
    marker: { size: 12 }
};

var data = [ trace1, trace2 ];

var config = {
    displaylogo: false,
    modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'],
    modeBarButtonsToAdd: [{
        name: 'toImage2',
        icon: Plotly.Icons.camera,
        click: function(gd) {
            Plotly.downloadImage(gd, {format: 'svg'})
        }
    }]
}

// let id = filename.indexOf(interest);
// console.log(interest);
// console.log(id);
// console.log(filename);
// var interest_file = index.map(i => fileID[i]);
// var interest_file = fileID.at(id);
// console.log(interest_file);
var layout = {
    xaxis: {
        // 'tickformat': ',d',
        title: "Rankings"
    },
    yaxis: {
        title: "Correlations"
        // range: [,8]
    },
    title: interest_id
}

Plotly.newPlot('region_rank', data, layout, config);
