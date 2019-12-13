import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['c0_d',
             'c1_d',
             'c2_d',
             'c3_d',
             'c4_d'
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
