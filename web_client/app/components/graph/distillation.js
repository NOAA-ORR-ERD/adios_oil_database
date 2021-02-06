import LineChart from './line-chart';
import { convertUnit } from 'adios-db/helpers/convert-unit';


export default class Distillation extends LineChart {
    xLabel = 'Mass Fraction (%)';
    yLabel = 'Vapor Temperature (\u00B0C)';
    xScaleMinRange = [0, 100];
    yScaleMinRange = [0];

    initData() {
        let cuts = (this.args.oil.distillation_data||{}).cuts;
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
            let weathered_cuts = cuts.filter((c) => {
                return (c.weathering === w &&
                        c.fraction &&
                        c.fraction.value &&
                        c.vapor_temp &&
                        c.vapor_temp.value);
            });

            data.push({
                values: weathered_cuts.map((c) => ([
                    convertUnit([c.fraction, '%']).value,
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
