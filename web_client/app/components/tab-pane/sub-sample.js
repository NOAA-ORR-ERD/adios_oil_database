import Component from '@glimmer/component';
import { action } from "@ember/object";
import slugify from 'ember-slugify';
import $ from 'jquery';

export default class SubSample extends Component {
    get sample() {
        return this.args.oil.samples.find(s => s.name === this.args.sampleName);
    }

    get sampleIndex() {
        // get an index of the current sample - to use one for component ID
        return this.args.oil.samples.findIndex(s => s.name === this.args.sampleName);
    }

    sampleTab() {
        if (this.args.sampleTab) {
            // get the last active subsample tab
            return this.args.sampleTab.slice('#'.length);
        }
        else {
            // just choose the first tab
            return slugify(this.args.oil.samples[0].name);
        }
    }

    categoryTab() {
        if(this.args.sampleTab && this.args.categoryTab &&
                this.args.categoryTab[this.args.sampleTab]) {
            return this.args.categoryTab[this.args.sampleTab].slice('#'.length)
        }
        else if (this.args.sampleTab) {
            // choose the first category in the current sample
            return this.args.sampleTab.slice('#'.length) + '-physical';
        }
        else {
            // just choose the first category in the fresh sample
            return 'fresh-oil-sample-physical';
        }
    }

    get navTabProperties() {
        return [
            ['physical', 'Physical Properties'],
            ['distillation', 'Distillation Data'],
            ['composition', 'Composition'],
            ['environmental', 'Environmental Behavior']
        ].map((item) => {
            let [tabName, label] = item;
            let ret = {
                'label': label,
                'id': this.sampleTab() + '-' + tabName + '-nav-tab',
                'href': '#' + this.sampleTab() + '-' + tabName,
                'aria-controls': this.sampleTab() + '-' + tabName,
            }

            if ('#' + this.categoryTab() === ret['href'])
            {
                return {
                    ...ret,
                    'class': 'nav-item nav-link active',
                    'aria-selected': true
                };
            }
            else {
                return {
                    ...ret,
                    'class': 'nav-item nav-link',
                    'aria-selected': false
                };
            }
        });
    }

    get tabPaneProperties() {
        return [
            ['physical', 'tab-pane/physical'],
            ['distillation', 'tab-pane/distillation'],
            ['composition', 'tab-pane/composition'],
            ['environmental', 'tab-pane/environmental']
        ].map((item) => {
            let [tabName, componentName] = item;
            let ret = {
                'id': this.sampleTab() + '-' + tabName,
                'aria-labelledby': this.sampleTab() + '-' + tabName + '-nav-tab',
                'componentName': componentName,
            }

            if (this.categoryTab() === ret['id'])
            {
                return {
                    ...ret,
                    'class': 'tab-pane fade active show'
                };
            }
            else {
                return {
                    ...ret,
                    'class': 'tab-pane fade'
                };
            }
        });
    }

    @action
    setEventShown(element) {
        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap tab.
        $(element).off("shown.bs.tab").on('shown.bs.tab', this, this.shown);
    }

    @action
    shown(event) {
        event.data.args.updateCategoryTab(event.currentTarget.hash);
    }

    @action
    submitSample() {
        this.args.submit(this.args.oil);
    }
}
