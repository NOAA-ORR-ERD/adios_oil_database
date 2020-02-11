import Controller from '@ember/controller';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class ShowController extends Controller {
    @tracked currentSampleTab = "#nav-fresh-oil-sample";
    @tracked currentCategoryTab = '#nav-physical-fresh-oil-sample';

    @action
    updateSampleTab(newTab) {
        this.currentSampleTab = newTab;
    }

    @action
    updateCategoryTab(newTab) {
        this.currentCategoryTab = newTab;
    }
}
