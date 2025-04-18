import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ButtonReviewStatus extends Component {
    @tracked dialogVisible = false;
    @tracked reviewStatus;
    
    reviewStatusLU = {
        'Not Reviewed': {
            'buttonType': 'danger',
            'spanStatusClass': 'p-1 status-error',
        },
        'Under Review': {
            'buttonType': 'warning',
            'spanStatusClass': 'p-1 status-warning',
        },
        'Review Complete': {
            'buttonType': 'success',
            'spanStatusClass': 'p-1 status-good',
        },
    };

    constructor() {
        super(...arguments);
        if (this.args.oil.review_status.status in this.reviewStatusLU) {
            this.reviewStatus = this.args.oil.review_status.status;
        }
        else {
            // We don't have a valid value for review status.  Use default
            this.reviewStatus = 'Not Reviewed';
        }
    }

    get reviewStatusProperties() {
        return this.reviewStatusLU[this.reviewStatus]
    }

    @action
    show_dialog(event) {
        this.dialogVisible = true;
    }

    @action
    close_dialog(event) {
        this.dialogVisible = false;
    }

    @action
    submit(oil) {
        this.args.submit(oil);
        this.dialogVisible = false;
    }
}
