import BaseComponent from '../common/base-component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";

export default class MeasurementGroupsButton extends BaseComponent {
    @tracked isShowingModal = false;
    @tracked valueObject;
    @tracked inputValue;

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        if (this.valueObject) {
            if (!Object.keys(this.valueObject).includes('groups')) {
                set(this.valueObject, 'groups', []);
            }

            this.inputValue = this.deepGet(this.valueObject, 'groups');
        }
        else {
            // No object was passed in.  We just set up a local input value.
            // We probably won't be able to persist any edits in this case.
            this.inputValue = [];
        }

        // Form component ID to which ember-modal-dialog needs to tether
        this.componentId = this.args.group.replace(/\s+/g, '-').toLowerCase() + 
            this.args.valueIndex;
    }

    @action
    showModal() {
        this.isShowingModal = true;
    }

    @action
    closeModal() {
        this.isShowingModal = false;
    }
}
