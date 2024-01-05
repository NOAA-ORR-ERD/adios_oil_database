import BaseComponent from '../common/base-component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

import moment from 'moment';


export default class LogChangesDlg extends BaseComponent {
    @tracked name;
    @tracked comment;

    get formFilledOut() {
        if (this.name && this.comment) {
            return true;
        }

        return false;
    }

    focusOKButton(event) {
        if (['change', 'focusout'].includes(event.type)
                && this.formFilledOut
                && this.okButton)
        {
            this.okButton.focus();
        }
    }

    @action
    updateName(event) {
        this.name = event.target.value;
        this.focusOKButton(event);
    }

    @action
    updateComment(event) {
        this.comment = event.target.value;
        this.focusOKButton(event);
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        let change_log = this.deepGet(this.args.oil, 'metadata.change_log');

        if (!change_log) {
            change_log = [];
        }

        this.deepSet(this.args.oil, 'metadata.change_log', change_log.concat({
            name: this.name,
            date: moment().local().toISOString(true),
            comment: this.comment
        }));

        this.args.submit(this.args.oil);
    }
}
