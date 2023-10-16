import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";


export default class ReportProblemQuery extends Component {
    @tracked dialogVisible;

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

    @action
    show_dialog(event) {
        this.dialogVisible = true;
    }

    @action
    close_dialog(event) {
        this.dialogVisible = false;
    }
}
