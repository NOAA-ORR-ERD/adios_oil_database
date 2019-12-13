import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);

        if (this.oil.alkylated_pahs != null &&
            ['biphenyl',
             'acenaphthylene',
             'acenaphthene',
             'anthracene',
             'fluoranthene',
             'pyrene',
             'perylene',
             'benz_a_anthracene',
             'benzo_b_fluoranthene',
             'benzo_k_fluoranthene',
             'benzo_e_pyrene',
             'benzo_a_pyrene',
             'benzo_ghi_perylene',
             'dibenzo_ah_anthracene',
             'indeno_1_2_3_cd_pyrene'
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

