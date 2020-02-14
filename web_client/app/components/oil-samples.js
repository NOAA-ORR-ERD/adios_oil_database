import Component from '@glimmer/component';
import { action } from "@ember/object";
import slugify from 'ember-slugify';
import $ from 'jquery';

export default class SubSample extends Component {

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

    get navTabProperties() {
        let savedTab = this.sampleTab();

        return this.args.oil.samples.map(s => {
            let tabName = slugify(s.name);
            let ret = {
                'name': s.name,
                'short_name': s.short_name,
                'id': tabName + '-nav-tab',
                'href': '#' + tabName,
                'aria-controls': tabName
            };

            if (savedTab === tabName) {
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
        let sampleTab = this.sampleTab();

        return this.args.oil.samples.map(s => {
            let tabName = slugify(s.name);
            let ret = {
                'name': s.name,
                'short_name': s.short_name,
                'id': tabName,
                'aria-labelledby': tabName + '-nav-tab'
            };


            if (sampleTab === tabName) {
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
        $(element).off("shown.bs.tab").on('shown.bs.tab', this, this.shown);
    }

    @action
    shown(event) {
        event.data.args.updateSampleTab(event.currentTarget.hash);
    }

    @action
    updateShortSampleName(idx) {
        this.args.oil.samples[idx].short_name = event.target.value;
        this.args.submit(this.args.oil);
    }

}
