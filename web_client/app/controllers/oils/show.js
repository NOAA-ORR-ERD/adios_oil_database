import OilsController from '../oils';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { service } from '@ember/service';

export default class ShowController extends OilsController {
    @tracked currentSampleTab = '';
    @tracked currentCategoryTab = {};
    @tracked changesMade = false;
    @tracked editable = false;

    @action
    setEditable(toggleState) {
        // We should only be able to unset edit mode if there are no changes
        // pending.
        if (toggleState === true || !this.changesMade) {
            this.editable = toggleState;
        }
    }

    @action
    updateSampleTab(newTab) {
        this.currentSampleTab = newTab;
    }

    @action
    updateCategoryTab(newTab) {
        if (this.currentSampleTab) {
            this.currentCategoryTab[this.currentSampleTab] = newTab;

            // trigger an update
            this.currentCategoryTab = this.currentCategoryTab;
        }
    }

    @action
    updateName(event) {
        let newName = event.target.value;
        this.model.metadata.name = newName;

        this.changesMade = true;
        this.model.save();
    }
}
