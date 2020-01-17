import { computed } from '@ember/object';

import { extent } from 'd3-array';
import { scaleLinear } from 'd3-scale';
import { axisLeft, axisBottom } from 'd3-axis';
import { format } from 'd3-format';
import { line } from 'd3-shape';

import LineChart from './line-chart';
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';


export default LineChart.extend({
  data: null,

  initData() {
    let cuts = this.oil.cuts;
    //cuts.map((c) => ([c.fraction.value, c.vapor_temp.value]));
    let data = [];

    let distinct_w;
    try {
      distinct_w = Array.from(new Set(cuts.map(c => c.weathering)));

      // We can optionally choose a particular weathered set py passing in
      // a weathered arg.  But it must match an existing one.
      if (distinct_w.includes(this.weathered)) {
          distinct_w = [this.weathered];
      }
    }
    catch(err) {
      distinct_w = [];
    }

    distinct_w.forEach(function(w) {
      let weathered_cuts = cuts.filter((c) => (c.weathering === w));

      data.push({
        name: w,
        values: weathered_cuts.map((c) => ([
          convertUnit([c.vapor_temp, 'C']).value,
          c.fraction.value
        ])),
        color: 'grey'
      });
    });

    if (data.length > 0) {
      data[0].color = 'green';
    }

    if (data.length > 1) {
      data.slice(-1)[0].color = 'red';
    }

    this.set('data', data);
  },

  xScale: computed('data.[]', 'chartWidth', function() {
    var data = this.get('data');
    var width = this.get('chartWidth');

    var xValues = data.length > 0 ? data[0].values.map((v) => (v[0])) : [0, 100];

    var minMax = extent(xValues);

    return scaleLinear()
      .domain(minMax)
      .range([0, width]);
  }),

  yScale: computed('data.[]', 'chartHeight', function() {
    var data = this.get('data');
    var height = this.get('chartHeight');

    var yValues = data.length > 0 ? data[0].values.map((v) => (v[1])) : [0, 1.0];
    var minMax = extent(yValues.concat(0.0, 1.0));

    return scaleLinear()
      .domain(minMax)
      .range([height, 0]);
  }),

  createXAxisElement: function() {
    let svg = this.get('chartSVG');
    var scale = this.get('xScale');
    var height = this.get('chartHeight');
    var width = this.get('chartWidth');

    var xAxis = axisBottom(scale)
      .tickFormat(format('.1f'))
      .tickSizeInner(4)
      .tickSizeOuter(0);

    svg.insert('g', ':first-child')
      .attr('class', 'chart__axis chart__axis--x')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis)
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    svg.selectAll('.chart__axis--x')
      .append("text")
      .attr("x", width / 2.0)
      .attr("y", 40)
      .attr("dy", ".5em")
      .attr("font-size", "1.5em")
      .attr("fill", "currentColor")
      .style("text-anchor", "middle")
      .text("Vapor Temperature (\u00B0C)");
  },

  createYAxisElement: function() {
    var svg = this.get('chartSVG');
    var scale = this.get('yScale');
    var height = this.get('chartHeight');
    var ticks = 6;

    var minMax = scale.domain();
    var diff = minMax[1] - minMax[0];
    var steps = diff / (ticks - 1);

    var tickValues = [];
    for (var i = 0; i < ticks; i++) {
      tickValues.push(minMax[0] + steps * i);
    }

    var yAxis = axisLeft(scale)
      .tickValues(tickValues)
      .tickFormat(format('.1f'))
      .tickSizeInner(6)
      .tickSizeOuter(6);

    svg.insert('g', ':first-child')
      .attr('class', 'chart__axis chart__axis--y')
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2.0)
      .attr("y", -40)
      .attr("dy", ".5em")
      .attr("font-size", "1.5em")
      .attr("fill", "currentColor")
      .style("text-anchor", "middle")
      .text("Fraction");
  },

  drawData: function() {
    var data = this.get('data');
    var xScale = this.get('xScale');
    var yScale = this.get('yScale');

    var svg = this.get('chartSVG');

    var chartLine = line()
      .x(function(d) {
        return xScale(d[0]);
      })
      .y(function(d) {
        return yScale(d[1]);
      });

    var lines = svg
      .selectAll('.line-chart__line__container')
      .data(data);

    // Append the new ones
    lines.enter()
      .append('g')
      .attr('class', 'line-chart__line__container')
      .append('svg:path')
      .attr('class', 'line-chart__line')
      .style('stroke', function(d) {
        return d.color;
      })
      .attr('d', function(d) {
        return chartLine(d.values);
      })
      .attr('fill', 'none');

    var circles = svg
      .selectAll("circle")
      .data(
        data.map((d) => (d.values)).flat()
        .map((p) => ( {'x': p[0], 'y': p[1]} ))
      );

    // Append the new ones
    circles
      .enter()
      .append("circle")
      .attr("cx", function (d) { return xScale(d.x); })
      .attr("cy", function (d) { return yScale(d.y); })
      .attr("r", 3)
      .style("fill", 'steelblue');
  },

  drawLegend: function() {
    var data = this.get('data');

    var svg = this.get('chartSVG');

    var legend = svg.append("g")
      .attr("class", "legend")
      .attr("height", 100)
      .attr("width", 100)
      .attr('transform', `translate(0, 0)`);

    legend.selectAll('rect')
      .data(data)
      .enter()
      .append("rect")
      .attr("x", 10)
      .attr("y", function(d, i){return 5 + (i * 10);})
      .attr("width", 10)
      .attr("height", 2)
      .style("fill", (d) => d.color);

    legend.selectAll('text')
      .data(data)
      .enter()
      .append("text")
      .attr("x", 25)
      .attr("y", function(d, i){return 5 + (i * 10);})
      .attr("dy", ".35em")
      .attr("font-size", ".7em")
      .attr("fill", "currentColor")
      .style("text-anchor", "start")
      .text(function(d) {return `w=${d.name}`;});
  },

});
