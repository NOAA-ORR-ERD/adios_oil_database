import Component from '@glimmer/component';

export default class ReportProblemOil extends Component {
    get destination() {
        return 'orr.adios@noaa.gov';
    }

    get subject() {
        return `Problem viewing oil ${this.args.oil.id}`;
    }

    get body() {
        return ('Dear ADIOS support team,\n\n' +
                'I noticed a problem viewing the oil record ' +
                `"${this.args.oil.metadata.name}" (${this.args.oil.id}).` +
                '\n\n<please state your problem>'
                );
    }
}
