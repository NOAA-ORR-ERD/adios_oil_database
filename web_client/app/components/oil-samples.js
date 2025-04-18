import Component from '@glimmer/component';
import { action } from "@ember/object";
import slugify from 'ember-slugify';
import $ from 'jquery';

export default class SubSample extends Component {

    get sampleTab() {
        if (this.args.sampleTab) {
            // get the last active subsample tab
            return this.args.sampleTab.slice('#'.length);
        }
        else {
            // just choose the first tab
            return slugify(this.args.oil.subSamples[0].metadata.short_name);
        }
    }

    get subsampleNavTabProperties() {
        let savedTab = this.sampleTab;
        let freshIndex = 0;

        return this.args.oil.sub_samples.map(s => {
            let sampleName = s.metadata.name;
            let sampleShortName = s.metadata.short_name;
            let tabName = slugify(sampleShortName);

            if (sampleName === 'Fresh Oil Sample') {
                if (freshIndex > 0) {
                    //sampleName = sampleName + `# ${freshIndex + 1}`;
                    //sampleShortName = sampleShortName + `# ${freshIndex + 1}`;
                    tabName = slugify(sampleShortName + `# ${freshIndex + 1}`);
                }
            }
            freshIndex += 1;

            let ret = {
                'name': sampleName,
                'short_name': sampleShortName,
                'id': tabName,
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

    get subsampleTabPaneProperties() {
        let sampleTab = this.sampleTab;
        let freshIndex = 0;

        return this.args.oil.sub_samples.map(s => {
            let sampleName = s.metadata.name;
            let sampleShortName = s.metadata.short_name;
            let tabName = slugify(sampleShortName);

            if (sampleName === 'Fresh Oil Sample') {
                if (freshIndex > 0) {
                    //sampleName = sampleName + `# ${freshIndex + 1}`;
                    //sampleShortName = sampleShortName + `# ${freshIndex + 1}`;
                    tabName = slugify(sampleShortName + `# ${freshIndex + 1}`);
                }
            }
            freshIndex += 1;

            let ret = {
                'id': tabName,
                'aria-labelledby': tabName + '-nav-tab',
                'name': sampleName,
                'short_name': sampleShortName,
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

    get extraNavTabProperties() {
        let savedTab = this.sampleTab;

        return [
            {'name': 'Attachments'}
        ].map(s => {
            let sampleName = s.name;
            let sampleShortName = s.name;
            let tabName = slugify(sampleShortName);

            let ret = {
                'name': sampleName,
                'short_name': sampleShortName,
                'id': tabName,
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

    get extraTabPaneProperties() {
        let sampleTab = this.sampleTab;

        return [
            ['attachments', 'tab-pane/attachments', 'Attachments'],
        ].map((item) => {
            let [tabName, componentName, label] = item;

            let ret = {
                'id': tabName,
                'label': label,
                'aria-labelledby': tabName + '-nav-tab',
                'componentName': componentName,
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
        event.data.args.updateSampleTab(event.currentTarget.hash);
    }

    @action
    onChangeTab(newTab) {
        this.args.updateSampleTab('#' + newTab);
    }

    @action
    updateShortSampleName(idx) {
        this.args.oil.sub_samples[idx].metadata.short_name = event.target.value;
        this.args.submit(this.args.oil);
    }

}
