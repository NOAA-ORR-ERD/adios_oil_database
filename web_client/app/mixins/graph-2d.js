import Mixin from '@ember/object/mixin';
import { computed } from '@ember/object';

import { extent } from 'd3-array';
import { scaleBand, scaleLinear } from 'd3-scale';
import { axisLeft, axisBottom } from 'd3-axis';
import { format } from 'd3-format';
import { select } from 'd3-selection';

export default Mixin.create({

  chartMargins: computed(function() {
      return {
        top: 20,
        right: 20,
        bottom: 60,
        left: 60
      };
  }),

  chartHeight: computed(function() {
    var height = 300;
    var margins = this.get('chartMargins');
    return height - margins.top - margins.bottom;
  }),

  chartWidth: computed(function() {
    var width = this.$().width();
    var margins = this.get('chartMargins');
    return width - margins.right - margins.left;
  }),

  xScale: computed(function() {
    var data = this.get('data');
    var width = this.get('chartWidth');

    return scaleBand()
      .domain(data.mapBy('name'))
      .range([0, width])
      .paddingOuter(1)
      .paddingInner(0.3);
  }),

  yScale: computed(function() {
    var data = this.get('data');
    var height = this.get('chartHeight');

    var allValues = extent(data, function(d) {
      return d.value;
    });

    return scaleLinear()
      .domain(allValues)
      .range([height, 0]);
  }),

  createChart: function() {
    // Clear the element, if there is something inside
    var chartEl = this.$().get(0);
    chartEl.innerHTML = '';

    this.addSVG();

    this.drawData();

    this.drawLegend();

    // Create the axes
    this.createXAxisElement();
    this.createYAxisElement();

  },

  createXAxisElement: function() {
    let svg = this.get('chartSVG');
    var scale = this.get('xScale');
    var height = this.get('chartHeight');

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
  },

  createYAxisElement: function() {
    var svg = this.get('chartSVG');
    var scale = this.get('yScale');
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
      .call(yAxis);
  },

  addSVG: function() {
    var el = this.$().get(0); // Get the actual DOM node, not the jQuery element

    var height = this.get('chartHeight');
    var width = this.get('chartWidth');
    var margins = this.get('chartMargins');

    var fullWidth = width + margins.left + margins.right;
    var fullHeight = height + margins.top + margins.bottom;

    var container = select(el).append('svg')
      .attr('class', `chart`)
      .attr('width', fullWidth)
      .attr('height', fullHeight)
      .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
      .attr('preserveAspectRatio', 'xMidYMid');

    let svg = container.append('g')
      .attr('transform', `translate(${margins.left},${margins.top})`);

    this.set('chartContainer', container);
    this.set('chartSVG', svg);
  },

});
