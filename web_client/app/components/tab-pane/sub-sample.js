import Component from '@glimmer/component';
import { action } from "@ember/object";
import slugify from 'ember-slugify';
import $ from 'jquery';

export default class SubSample extends Component {
    get sample() {
        let ret = this.args.oil.sub_samples.find(s => s.metadata.short_name === this.args.sampleName);

        // create some intermediate parts of our oil structure.
        // If we don't do this, our edit controls won't have anything in the
        // record to attach to.
        if (!ret.physical_properties) {
            ret.physical_properties = {};
        }

        if (!ret.distillation_data) {
            ret.distillation_data = {'cuts': []};
        }

        return ret;
    }

    get sampleIndex() {
        // get an index of the current sample - to use one for component ID
        return this.args.oil.sub_samples.findIndex(s => s.metadata.short_name === this.args.sampleName);
    }

    sampleTab() {
        if (this.args.sampleTab) {
            // get the last active subsample tab
            return this.args.sampleTab.slice('#'.length);
        }
        else {
            // just choose the first tab
            return slugify(this.args.oil.sub_samples[0].metadata.short_name);
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
            return 'fresh-oil-physical';
        }
    }

    visible(currentTab) {
        // Which tab is visible at any given state?
        // - When we switch to a sample tab for the first time, it's sampletab->physical
        // - When we switch to it after that, it's sampletab->lastactive
        let ret = false;
        let currentSampleTab = '#' + slugify(this.sample.metadata.short_name);

        if (currentSampleTab === this.args.sampleTab) {
            // we are at least on the right sample
            // is it the right category?
            if (typeof this.args.categoryTab[currentSampleTab] === 'undefined') {
                // we choose physical as the default
                if (currentTab === 'physical') {
                    ret = true;
                }
            }
            else if (this.args.categoryTab[currentSampleTab] === currentSampleTab + '-' + currentTab)
            {
                // we choose the last active category tab
                ret = true;
            }
        }

        return ret;
    }

    get tabPaneProperties() {
        return [
            ['physical', 'tab-pane/physical', 'Physical Properties'],
            ['distillation', 'tab-pane/distillation', 'Distillation Data'],
            ['compounds', 'tab-pane/compounds', 'Compounds'],
            ['bulk-composition', 'tab-pane/bulk-composition', 'Bulk Composition'],
            ['environmental', 'tab-pane/environmental', 'Environmental Behavior'],
            ['industry-properties', 'tab-pane/industry-properties', 'Industry Properties'],
            ['metadata', 'tab-pane/subsample-metadata', 'Metadata']
        ].map((item) => {
            let [tabName, componentName, label] = item;

            let ret = {
                'id': this.sampleTab() + '-' + tabName,
                'label': label,
                'aria-labelledby': this.sampleTab() + '-' + tabName + '-nav-tab',
                'componentName': componentName,
                'visible': this.visible(tabName)
            }

            if (ret['visible']) {
                return {
                    ...ret,
                    'class': 'tab-pane active show'
                };
            }
            else {
                return {
                    ...ret,
                    'class': 'tab-pane'
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
        $(element).off("shown.bs.tab").on('shown.bs.tab', this, this.shown);  // eslint-disable-line ember/no-jquery
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
