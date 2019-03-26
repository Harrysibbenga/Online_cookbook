console.log('Loaded')
queue()
    .defer(d3.json, "/onlinecookbook/recipes")
    .await(makeGraphs);

function makeGraphs(error, recipesData) {
    console.log(recipesData)
    var ndx = crossfilter(recipesData);
    show_category_chart(ndx);
    show_origin_pie_chart(ndx);
    
    dc.renderAll();
}

function show_category_chart(ndx) {
    var dim = ndx.dimension(dc.pluck('category'));
    var group = dim.group();

    dc.barChart("#category-chart")
        .width(400)
        .height(300)
        .margins({ top: 10, right: 50, bottom: 30, left: 50 })
        .dimension(dim)
        .group(group)
        .transitionDuration(1500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .xAxisLabel("Category")
        .yAxis().ticks(1);
}

function show_origin_pie_chart(ndx) {
    var dim = ndx.dimension(dc.pluck('origin'));
    var group = dim.group();

    dc.pieChart("#origin-chart")
        .height(300)
        .radius(150)
        .transitionDuration(1500)
        .dimension(dim)
        .group(group)
}