import Component from '@ember/component';
import { computed } from '@ember/object';

import { extent } from 'd3-array';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { line } from 'd3-shape';

import Graph2d from 'ember-oil-db/mixins/graph-2d';

export default Component.extend(Graph2d, {
  data: null,

  init() {
    this._super(...arguments);
    this.initData();
  },

  initData() {
    this.set('data', [{
       name: 'John',
       values: [7512, 8093, 14731, 10082],
       color: 'red'
     },
     {
       name: 'Anne',
       values: [9923, 9789, 8309, 10810],
       color: 'green'
     },
     {
       name: 'Robert',
       values: [6039, 7093, 4020, 9501],
       color: 'blue'
     }]);
  },

  xScale: computed('data.[]', 'chartWidth', function() {
    var data = this.get('data');
    var width = this.get('chartWidth');

    var firstItem = data[0];
    var positions = firstItem.values.map(function(item, i) {
      return i;
    });

    var widthPiece = width / (positions.length - 1);
    var positionPoints = positions.map(function(position) {
      return widthPiece * position;
    });

    return scaleOrdinal()
      .domain(positions)
      .range(positionPoints);
  }),

  yScale: computed('data.[]', 'chartHeight', function() {
    var data = this.get('data');
    var height = this.get('chartHeight');

    var values = [];
    data.forEach(function(d) {
      values.pushObjects(d.values);
    });
    var minMax = extent(values);

    return scaleLinear()
      .domain(minMax)
      .range([height, 0]);
  }),

  drawData: function() {
    var data = this.get('data');
    var x = this.get('xScale');
    var y = this.get('yScale');

    var svg = this.get('chartSVG');

    var chartLine = line()
      .x(function(d, i) {
        return x(i);
      })
      .y(function(d) {
        return y(d);
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
  },

  drawLegend: function() {
    // no legend for the basic line chart.
  },

  // -----------------------------------------------------------------------
  // LIFECYCLE HOOKS
  // These are special functions that are called by ember at different stages
  // of the component's lifecycle.
  // -----------------------------------------------------------------------

  didInsertElement: function() {
    this.createChart();
  }

});
