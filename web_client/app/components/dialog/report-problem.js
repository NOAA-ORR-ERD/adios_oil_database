import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import $ from 'jquery';


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
    setModalEvents(element) {
        // Note: Bootstrap modals can not be modified with event handlers until
        //       the elements are completely rendered.  So we can't add an 'on'
        //       handler in the template like you would normally be able to do.
        //       So we add a did-insert handler in the template, attaching it
        //       to this function.
        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap modal.
        //       Don't believe me?  https://stackoverflow.com/questions/24211185/twitter-bootstrap-why-do-modal-events-work-in-jquery-but-not-in-pure-js
        $(element).on('shown.bs.modal', this.shown);  // eslint-disable-line ember/no-jquery
    }

    @action
    shown(event) {
        event.currentTarget.querySelector('input').focus();
    }

    @action
    updateSubject(event) {
        this.subject = event.target.value;
    }

    @action
    updateBody(event) {
        this.body = event.target.value;
    }

}
