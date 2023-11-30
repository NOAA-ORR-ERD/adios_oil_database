import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";


export default class ReportProblemDlg extends Component {
    @tracked destination;
    @tracked subject;
    @tracked body;

    constructor() {
        super(...arguments);

        this.destination = this.args.destination;
        this.subject = this.args.subject;
        this.body = this.args.body;
    }

    get formFilledOut() {
        if (this.destination && this.subject && this.body) {
            return true;
        }

        return false;
    }

    get body_as_uri_component() {
        return encodeURIComponent(this.body);
    }

     @action
    updateSubject(event) {
        this.subject = event.target.value;
    }

    @action
    updateBody(event) {
        this.body = event.target.value;
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        this.args.close();
    }

}
