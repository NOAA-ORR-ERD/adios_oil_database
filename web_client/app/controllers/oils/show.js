import Controller from '@ember/controller';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ShowController extends Controller {
    @tracked currentSampleTab = '#fresh-oil-sample';
    @tracked currentCategoryTab = {
        '#fresh-oil-sample': '#fresh-oil-sample-physical'
    };

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
}
