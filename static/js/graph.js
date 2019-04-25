queue()
    .defer(d3.json, "/onlinecookbook/recipes")
    .await(makeGraphs);

function makeGraphs(error, recipesData) {
    var ndx = crossfilter(recipesData);
    show_category_chart(ndx);
    show_origin_pie_chart(ndx);
    show_diet_distribution(ndx);
    show_cuisine_chart(ndx);
    dc.renderAll();
}

function show_category_chart(ndx) {
    var dim = ndx.dimension(dc.pluck('category'));
    var group = dim.group();

    dc.barChart("#category-chart")
        .width(400)
        .height(300)
        .dimension(dim)
        .group(group)
        .transitionDuration(1500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .xAxisLabel("Categories")
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
        .group(group);
}

function show_diet_distribution(ndx) {

    function type_by_diet(dimension, diet) {
        return dimension.group().reduce(
            function add_fact(p, v) {
                p.total++;
                if (v.diet == diet) {
                    p.match++;
                }
                return p;
            },

            function remove_fact(p, v) {
                p.total--;
                if (v.diet == diet) {
                    p.match--;
                }
                return p;
            },

            function initialise() {
                return { total: 0, match: 0 }; 
            }
        );
    }
    
    var dim = ndx.dimension(dc.pluck("type"));
    var type_by_meat = type_by_diet(dim, "Meat");
    var type_by_vegetarian = type_by_diet(dim, "Vegetarian");
    var type_by_pescatarian = type_by_diet(dim, "Pescatarian");
    var type_by_vegan = type_by_diet(dim, "Vegan");


    dc.barChart("#diet-distribution")
        .width(400)
        .height(300)
        .dimension(dim)
        .group(type_by_meat, "Meat")
        .stack(type_by_vegetarian, "Vegetarian")
        .stack(type_by_pescatarian, "Pescatarian")
        .stack(type_by_vegan, "Vegan")
        .valueAccessor(function(d) {
            if (d.value.total > 0) {
                return (d.value.match / d.value.total) * 100;
            }
            else {
                return 0;
            }
        })
        .transitionDuration(1500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .xAxisLabel("Types of Food")
        .legend(dc.legend().x(320).y(20).itemHeight(15).gap(5))
}

function show_cuisine_chart(ndx) {
    var dim = ndx.dimension(dc.pluck('user'));
    var group = dim.group();

    dc.barChart("#users-chart")
        .width(400)
        .height(300)
        .dimension(dim)
        .group(group)
        .transitionDuration(1500)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .xAxisLabel("Users")
        .yAxis().ticks(1);
}