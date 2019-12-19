import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['c0_f',
             'c1_f',
             'c2_f',
             'c3_f',
             'c4_f'
             ].some(i => {
                 return this.oil.alkylated_pahs[i] != null;
             }))
        {
            this.set('anyDataPresent', true);
        }
        else {
            this.set('anyDataPresent', false);
        }
    }
});
