import Component from '@ember/component';
import $ from 'jquery';

export default Component.extend({

    didRender() {
        this._super(...arguments);

        // clear the slate
        this.element.querySelectorAll('a[data-toggle="tab"][tab-level="0"]')
        .forEach(i => {
            i.classList.remove('active');
            i.setAttribute('aria-selected', false);
        });

        this.element.querySelectorAll('.tab-pane[tab-level="0"]')
        .forEach(i => {
            i.classList.remove('active', 'show');
        });


        if (this.sampleTab &&
            this.element.querySelector(this.sampleTab))
        {
            let elem = this.element.querySelector(`a[href="${this.sampleTab}"]`);
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active');

            this.element.querySelector(this.sampleTab)
                .classList.add('active', 'show');
        }
        else {
            // set the default tab to the first one
            let elem = this.element.querySelector('a[data-toggle="tab"][tab-level="0"]')
            elem.setAttribute('aria-selected', true);
            elem.classList.add('active');

            this.element.querySelector('.tab-pane[tab-level="0"]')
                .classList.add('active', 'show');
        }

        // Note: Ember doesn't want you to use JQuery for some purity reason,
        //       and it throws warnings when the app starts.
        //       Unfortunately, JQuery is the only way to add an event listener
        //       to a bootstrap tab.
        $(this.element).find('a[data-toggle="tab"][tab-level="0"]')
                       .off("shown.bs.tab")
                       .on('shown.bs.tab', this, this.actions.shown);
    },

    actions: {
        shown(event) {
            event.data.updateSampleTab(event.currentTarget.hash);
        },

        updateShortSampleName(idx) {
            this.oil.samples[idx].short_name = event.target.value;
            this.submit(this.oil);
        }
    }

});
