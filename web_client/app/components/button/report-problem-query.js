import Component from '@glimmer/component';

export default class ReportProblemQuery extends Component {
    get destination() {
        return 'orr.adios@noaa.gov';
    }

    get subject() {
        return 'Problem using oil query table';
    }

    get body() {
        return ('Dear ADIOS support team,\n\n' +
                'I noticed a problem when using the oil query table.' +
                '\n\n<please state your problem>'
                );
    }
}
