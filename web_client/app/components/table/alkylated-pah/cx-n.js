import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['c0_n',
             'c1_n',
             'c2_n',
             'c3_n',
             'c4_n'
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
