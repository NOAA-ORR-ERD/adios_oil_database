import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import $ from 'jquery';

export default class SubSample extends Component {
    get sample() {
        return this.args.oil.samples.find(s => s.name === this.args.sampleName);
    }

    get sampleIndex() {
        // get an index of the current sample - to use one for component ID
        return this.args.oil.samples.findIndex(s => s.name === this.args.sampleName);
    }

    @action
    setToLastNavTab(element) {
        // clear the slate
        element.querySelectorAll('a[data-toggle="tab"][tab-level="1"]')
        .forEach(i => {
            i.classList.remove('active');
            i.setAttribute('aria-selected', false);
        });

        if (this.args.categoryTab &&
            element.querySelector(`a[href="${this.args.categoryTab}"]`))
        {
            // set our last active tab
            let elem = element.querySelector(`a[href="${this.args.categoryTab}"]`);
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active');
        }
        else {
            // set the default tab to the first one
            let elem = element.querySelector('a[data-toggle="tab"][tab-level="1"]')
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active');
        }

        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap tab.
        $(element).find('a[data-toggle="tab"][tab-level="1"]')
                  .off("shown.bs.tab")
                  .on('shown.bs.tab', this, this.shown);
    }

    @action
    setToLastTabPane(element) {
        // clear the slate
        element.querySelectorAll('.tab-pane[tab-level="1"]')
        .forEach(i => {
            i.classList.remove('active', 'show');
        });

        if (this.args.categoryTab &&
                element.querySelector(this.args.categoryTab))
        {
            element.querySelector(this.args.categoryTab)
                .classList.add('active', 'show');
        }
        else {
            // set the default tab to the first one
            let elem = element.querySelector('.tab-pane[tab-level="1"]')
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active', 'show');
        }
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
