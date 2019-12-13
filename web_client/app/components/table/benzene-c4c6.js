import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);
        
        if (this.oil.benzene != null &&
            ['amylbenzene',
             'propylbenzene',
             'isopropylbenzene',
             'isobutylbenzene',
             'n_hexylbenzene',
             '_1_2_3_trimethylbenzene',
             '_1_2_4_trimethylbenzene',
             '_1_3_5_trimethylbenzene',
             '_2_ethyltoluene',
             '_3_4_ethyltoluene',
             '_1_methyl_2_isopropylbenzene',
             '_1_2_dimethyl_4_ethylbenzene'
             ].some(i => {
                 return this.oil.benzene[i] != null;
             }))
        {
            this.set('allDataPresent', true);
        }
        else {
            this.set('allDataPresent', false);
        }
    }
});
