import Component from '@ember/component';

export default Component.extend({
    didReceiveAttrs() {
        this._super(...arguments);
        
        if (this.oil.benzene != null &&
            ['toluene',
             'ethylbenzene',
             'm_p_xylene',
             'o_xylene'
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
