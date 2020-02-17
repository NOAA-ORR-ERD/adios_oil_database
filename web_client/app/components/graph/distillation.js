import { line } from 'd3-shape';

import LineChart from './line-chart';
import { convertUnit } from 'ember-oil-db/helpers/convert-unit';


export default class Distillation extends LineChart {
    xLabel = 'Mass Fraction (%)';
    yLabel = 'Vapor Temperature (\u00B0C)';
    xScaleMinRange = [0];
    yScaleMinRange = [0];

    initData() {
        let cuts = this.args.oil.cuts;
        let data = [];
        let label;

        if (typeof this.args.oil.fraction_weathered !== 'undefined') {
            label = 'weathered=' + this.args.oil.fraction_weathered;
        }
        else if (typeof this.args.oil.boiling_point_range !== 'undefined') {
            label = 'BP range=' + this.args.oil.boiling_point_range;
        }

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
            let weathered_cuts = cuts.filter((c) => {
                return (c.weathering === w &&
                        c.fraction &&
                        c.fraction.value &&
                        c.vapor_temp &&
                        c.vapor_temp.value);
            });

            data.push({
                name: label,
                values: weathered_cuts.map((c) => ([
                    c.fraction.value,
                    convertUnit([c.vapor_temp, 'C']).value
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

        this.data = data;
    }

    drawData() {
        let data = this.data;
        let xScale = this.xScale;
        let yScale = this.yScale;

        let svg = this.chartSVG;

        let chartLine = line()
        .x(function(d) {
            return xScale(d[0]);
        })
        .y(function(d) {
            return yScale(d[1]);
        });

        let lines = svg
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

        let circles = svg
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
    }

}
