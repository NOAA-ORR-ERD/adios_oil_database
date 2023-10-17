import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";


export default class ReportProblemOil extends Component {
    @tracked dialogVisible = false;

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

    @action
    show_dialog(event) {
        this.dialogVisible = true;
    }

    @action
    close_dialog(event) {
        this.dialogVisible = false;
    }
}
