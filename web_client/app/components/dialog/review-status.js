import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";
import { ref } from 'ember-ref-bucket';
import moment from 'moment';

export default class DialogReviewStatus extends Component {
    valid_status_values = [
        "Not Reviewed",
        "Under Review",
        "Review Complete",
    ];

    // @ref gives us a reference to a piece of our template
    @ref("okButton") okButton;

    @tracked status;
    @tracked reviewers;
    @tracked notes;


    constructor() {
        super(...arguments);

        this.status = this.args.oil.review_status.status;
        this.reviewers = this.args.oil.review_status.reviewers;
        this.notes = this.args.oil.review_status.notes;
    }

    get formFilledOut() {
        if (this.reviewers && this.notes) {
            return true;
        }

        return false;
    }

    @action
    updateStatus(event) {
        this.status = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    updateReviewers(event) {
        this.reviewers = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    updateNotes(event) {
        this.notes = event.target.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        let reviewStatus = {
            status: this.status,
            reviewers: this.reviewers,
            review_date: moment().local().format("YYYY-MM-DDTHH:mm:ss"),
            notes: this.notes
        };

        this.args.submit(reviewStatus);
    }

}
