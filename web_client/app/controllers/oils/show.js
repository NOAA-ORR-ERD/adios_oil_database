import Controller from '@ember/controller';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ShowController extends Controller {
    @tracked currentSampleTab = '#fresh-oil-sample';
    @tracked currentCategoryTab = {
        '#fresh-oil-sample': '#fresh-oil-sample-physical'
    };
    @tracked changesMade = false;
    @tracked editable = false;

    get canModifyDb() {
        return this.capabilities.firstObject.can_modify_db == 'true';
    }

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
