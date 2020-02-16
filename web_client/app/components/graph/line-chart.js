import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

import { extent } from 'd3-array';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { axisLeft, axisBottom } from 'd3-axis';
import { format } from 'd3-format';
import { select } from 'd3-selection';
import { line } from 'd3-shape';


export default class LineChart extends Component {
    // There are a number of configuration parameters for this component
    // that can be either passed as a parameter in the .hbs template,
    // or set by subclassing this component and defining a custom default value.
    //
    // Configurable Items:
    //    - aspectRatio: If a size is not supplied, the graph will choose a
    //                   width based on the existing dom element, and then
    //                   choose a relative height based on the aspect ratio
    //    - size: An object that sets the size of the graph. The default will
    //            be {width: <domWidth>, height: <domWidth/aspectRatio>}
    //    - margins: An object representing the margins between the border
    //               and the drawing area of the graph.  The default will be
    //               {top: 20, right: 20, bottom: 60, left: 60}
    //    - xLabel: A string value to be used as a label for the X axis
    //    - yLabel: A string value to be used as a label for the Y axis
    //    - yScaleMinRange: A list of numbers that set the minimum numeric
    //                      range for the Y axis.  Typically this would be a
    //                      2-tuple, but it can have a tuple with just a
    //                      single number representing a min or a max for
    //                      the range.
    //    - xScaleMinRange: A list of numbers that set the minimum numeric
    //                      range for the X axis.  Typically this would be a
    //                      2-tuple, but it can have a tuple with just a
    //                      single number representing a min or a max for
    //                      the range.
    //    - legendPosition: Which corner to put the legend.  Can be one of
    //                      {'top-left', 'top-right',
    //                       'bottom-left', 'bottom-right'}
    @tracked data = null;

    constructor() {
        super(...arguments);
        this.initData();
    }

    initData() {
        this.data = [{
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
        }];
    }

    get aspectRatio() {
        if (this.args.aspectRatio) {
            return this.args.aspectRatio;
        }
        else {
            return 3.0 / 2.0;  // default
        }
        
    }

    get chartMargins() {
        if (this.args.margins) {
            return this.args.margins;
        }
        else {
            return {
                top: 20,
                right: 20,
                bottom: 60,
                left: 60
            };
        }
    }

    get chartSize() {
        let m = this.chartMargins;

        if (this.args.size) {
            let marginSizes = [
                ['left','right'],
                ['top','bottom']
                ].map(d => d.map(k => m[k]).reduce((i, j) => i + j));

            return Object.fromEntries([
                'width',
                'height'
                ].map((s, i) => {
                    return [s, this.args.size[s] - marginSizes[i]];
                }));
        }
        else {
            let width = this.clientWidth - m.right - m.left;
            let height = (this.clientWidth / this.aspectRatio) - m.top - m.bottom;

            return {
                width: width,
                height: height
            };
        }
    }

    get chartHeight() {
        return this.chartSize.height;
    }

    get chartWidth() {
        return this.chartSize.width;
    }

    get xScaleRange() {
        if (this.args.xScaleMinRange) {
            return this.args.xScaleMinRange;
        }
        else if (this.xScaleMinRange) {
            return this.xScaleMinRange
        }
        else {
            return [];
        }
    }

    get xScale() {
        let xValues = [].concat(...this.data.map(d => d.values));

        if (xValues.every(i => i.length === 2)) {
            // array of x/y pairs.  Get the x values
            xValues = xValues.map(i => i[0]).concat(...this.xScaleRange);
        }
        else {
            // Assume we have a bunch of y scalars.  Generate indexes of y
            xValues = Array(Math.max(...this.data.map(d => d.values.length)))
            .fill().map((_, i) => i)
            .concat(...this.xScaleRange);
        }

        if (xValues.length === 0) {
            xValues = [0];  // gotta have at least one point
        }

        return scaleLinear().domain(extent(xValues)).range([0, this.chartWidth]);
    }

    get yScaleRange() {
        if (this.args.yScaleMinRange) {
            return this.args.yScaleMinRange;
        }
        else if (this.yScaleMinRange) {
            return this.yScaleMinRange
        }
        else {
            return [];
        }
    }

    get yScale() {
        let yValues = [].concat(...this.data.map(d => d.values));

        if (yValues.every(i => i.length === 2)) {
            // array of x/y pairs.  Get the y values
            yValues = yValues.map(i => i[1]).concat(...this.yScaleRange);
        }
        else {
            yValues = yValues.concat(...this.yScaleRange);
        }
        
        if (yValues.length === 0) {
            yValues = [0];  // gotta have at least one point
        }

        return scaleLinear().domain(extent(yValues)).range([this.chartHeight, 0]);
    }

    @action
    createChart(element) {
        // Clear the element, if there is something inside
        element.innerHTML = '';

        this.addSVG(element);

        this.drawData(element);

        this.createXAxisElement();

        let xLabel;
        if (this.args.xLabel) {
            xLabel = this.args.xLabel;
        }
        else if (this.xLabel) {
            xLabel = this.xLabel;
        }

        if (xLabel) {
            this.createXAxisLabel(xLabel);
        }

        this.createYAxisElement();

        let yLabel;
        if (this.args.yLabel) {
            yLabel = this.args.yLabel;
        }
        else if (this.yLabel) {
            yLabel = this.yLabel;
        }

        if (yLabel) {
            this.createYAxisLabel(yLabel);
        }

        if (this.data.every(d => d.hasOwnProperty('name'))) {
            this.drawLegend(element);
        }
    }

    @action
    addSVG(element) {
        var el = element;
        this.clientWidth = element.clientWidth;

        var height = this.chartHeight;
        var width = this.chartWidth;
        var margins = this.chartMargins;

        var fullWidth = width + margins.left + margins.right;
        var fullHeight = height + margins.top + margins.bottom;

        var container = select(el).append('svg')
        .attr('class', 'chart')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMid');

        let svg = container.append('g')
        .attr('transform', `translate(${margins.left}, ${margins.top})`);

        this.chartContainer = container;
        this.chartSVG = svg;
    }

    drawData() {
        var data = this.data;
        var x = this.xScale;
        var y = this.yScale;

        var svg = this.chartSVG;

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
    }

    get legendXYPosition() {
        if (this.args.legendPosition) {
            return this.args.legendPosition;
        }
        else if (this.legendPosition) {
            return this.legendPosition
        }
        else {
            return 'default';
        }        
    }

    drawLegend() {
        let translation;

        switch (this.legendXYPosition) {
        case 'top-left':
            translation = `translate(0, 0)`
            break;
        case 'top-right':
            translation = `translate(${this.chartWidth-100}, 0)`;
            break;
        case 'bottom-left':
            translation = `translate(0, ${this.chartHeight-20})`
            break;
        case 'bottom-right':
            translation = `translate(${this.chartWidth-100}, ${this.chartHeight-20})`;
            break;
        default:
            translation = `translate(0, 0)`;
            break;
        }

        let legend = this.chartSVG.append("g")
        .attr("class", "legend")
        .attr("height", 100)
        .attr("width", 100)
        .attr('transform', translation);

        legend.selectAll('rect')
        .data(this.data)
        .enter()
        .append("rect")
        .attr("x", 10)
        .attr("y", function(d, i){return 5 + (i * 10);})
        .attr("width", 10)
        .attr("height", 2)
        .style("fill", (d) => d.color);

        legend.selectAll('text')
        .data(this.data)
        .enter()
        .append("text")
        .attr("x", 25)
        .attr("y", function(d, i){return 5 + (i * 10);})
        .attr("dy", ".35em")
        .attr("font-size", ".7em")
        .attr("fill", "currentColor")
        .style("text-anchor", "start")
        .text(function(d) {return d.name;});
    }

    createXAxisElement() {
        let svg = this.chartSVG;
        var scale = this.xScale;
        var height = this.chartHeight;

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
    }

    createXAxisLabel(label) {
        let svg = this.chartSVG;

        svg.selectAll('.chart__axis--x')
        .append("text")
        .attr("x", this.chartWidth / 2.0)
        .attr("y", 40)
        .attr("dy", ".5em")
        .attr("font-size", "1.5em")
        .attr("fill", "currentColor")
        .style("text-anchor", "middle")
        .text(label);
    }

    createYAxisElement() {
        var svg = this.chartSVG;
        var scale = this.yScale;
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
    }

    createYAxisLabel(label) {
        let svg = this.chartSVG;

        svg.selectAll('.chart__axis--y')
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -this.chartHeight / 2.0)
        .attr("y", -50)
        .attr("dy", ".5em")
        .attr("font-size", "1.5em")
        .attr("fill", "currentColor")
        .style("text-anchor", "middle")
        .text(label);
    }
}
