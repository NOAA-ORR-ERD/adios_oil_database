import Component from '@ember/component';
import { set } from "@ember/object";

export default Component.extend({

    init(){
        this._super(...arguments);
    },
    
    actions: {
        onSubmit(densitiesValue) {
            let oil = this.get('oil');
            set(oil, 'densities', densitiesValue);
            this.submit(oil);
        }
    }
});
