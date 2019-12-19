import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['c0_c',
             'c1_c',
             'c2_c',
             'c3_c',
             'c4_c'
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
