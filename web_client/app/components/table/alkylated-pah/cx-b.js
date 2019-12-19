import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['c0_b',
             'c1_b',
             'c2_b',
             'c3_b',
             'c4_b'
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
