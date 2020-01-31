import Component from '@ember/component';
import $ from 'jquery';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        let sampleName = this.get('sampleName');
        let samples = this.get('oil').samples;

        let sample = samples.find( (s) => {
            return s.name === sampleName;
        });

        // get an index of the current sample - to use one for component ID
        let sampleIndex = this.get('oil').samples.findIndex(
            xSample => xSample.name === sampleName);

        this.set('sample', sample);
        this.set('sampleIndex', sampleIndex);
    },

    didInsertElement() {
        this._super(...arguments);

        if (this.categoryTab &&
            this.element.querySelector(this.categoryTab))
        {
            this.element.querySelectorAll('.tab-pane').forEach(i => {
                i.classList.remove('active', 'show');
            });
            this.element.querySelectorAll('a[data-toggle="tab"]').forEach(i => {
                i.classList.remove('active');
                i.setAttribute('aria-selected', false);
            });

            let elem = this.element.querySelector(`a[href="${this.categoryTab}"]`);
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active');

            this.element.querySelector(this.categoryTab)
                .classList.add('active', 'show');
        }
        else {
            // just use the default behavior
            this.element.querySelectorAll('.tab-pane').forEach(i => {
                if (!i.classList.contains('show')) {
                    i.classList.remove('active');
                }
            });
        }

        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap tab.
        $(this.element).find('a[data-toggle="tab"]')
                       .off("shown.bs.tab")
                       .on('shown.bs.tab', this, this.actions.shown);

    },

    actions: {
        shown(event) {
            event.data.updateCategoryTab(event.currentTarget.hash);
        },

        submitSample() {
            let oil = this.get('oil');
            // let samples =  oil.samples;
            // samples[this.sampleIndex] = sample;
            // oil.set('samples', samples);
            this.submit(oil);
        }
    }
});
