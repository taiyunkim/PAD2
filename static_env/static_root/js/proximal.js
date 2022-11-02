// file: our_static/js/proximal.js
// author: Taiyun Kim
// date: Mar 2016
// plots proximal heatmap with dendrogram using Plotly.js

var i;
var trace = [];

if (json_data['proximal_dendrogram'] != "None") {
    var proximal_dendrogram = json_data['proximal_dendrogram'];

    for (i = 0;  i < proximal_dendrogram['dcoord'].length; i++){
        var t = {
            x: proximal_dendrogram['icoord'][i],
            y: proximal_dendrogram['dcoord'][i],
            marker: {color: "rgb(0,204,102)"}, 
            mode: "lines", 
            type: "scatter", 
            xaxis: "xs", 
            yaxis: "y2"
        };
        trace.push(t);
    }
    for (i = 0;  i < proximal_dendrogram['dcoord'].length; i++){
        var t = {
            x: proximal_dendrogram['dcoord'][i],
            y: proximal_dendrogram['icoord'][i],
            marker: {color: "rgb(0,204,102)"}, 
            mode: "lines", 
            type: "scatter", 
            xaxis: "x2", 
            yaxis: "ys"
        };
        trace.push(t);
    }
}

var m = [5.0];
var increment = 10.0;
for (i = 1; i < json_data['matrix_size']; i++) {
    m.push(m[i-1] + increment)
}

var trace00 = [
    {
        z: json_data['proximal_matrix'],
        x: m,
        y: m,
        type: 'heatmap',
        zmin: 0,
        zmax: 0.2,
    }
];
var data = trace.concat(trace00);
var layout = {
    autosize: true, 
    bargap: 0, 
    height: document.getElementById('heatmap').offsetWidth - 150, 
    hovermode: "closest", 
    showlegend: false, 
    width: document.getElementById('heatmap').offsetWidth, 
    margin: {
        l: 150,
        r: 50,
        b: 150,
        t: 50,
        pad: 2
    },
    xaxis: {
        autotick: false, 
        domain: [0.1, 0.85], 
        dtick: 1, 
        mirror: "allticks", 
        rangemode: "tozero", 
        showgrid: false, 
        showline: true, 
        showticklabels: true, 
        tickmode: "array", 
        ticks: "inside", 
        ticktext: json_data['p_filename'], 
        tickvals: m,
        type: "linear", 
        zeroline: false
    }, 
    xaxis2: {
        domain: [0.85, 1], 
        showgrid: false, 
        zeroline: false
    }, 
    yaxis: {
        autotick: false, 
        domain: [0, 0.86], 
        dtick: 1, 
        mirror: "allticks", 
        rangemode: "tozero", 
        showgrid: false, 
        showline: true, 
        showticklabels: true, 
        tickmode: "array", 
        ticks: "inside", 
        ticktext: json_data['p_filename'],
        tickangle: 0,
        tickvals: m, 
        type: "linear", 
        zeroline: false
    }, 
    yaxis2: {
        domain: [0.85, 1], 
        showgrid: false, 
        zeroline: false
    }
};

// Plot
Plotly.newPlot('proximal', data, layout, {displaylogo: false});