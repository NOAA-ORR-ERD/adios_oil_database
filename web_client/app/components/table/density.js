import Component from '@ember/component';
import { set } from "@ember/object";

export default Component.extend({

    init(){
        this._super(...arguments);
    },
    
    actions: {
        onSubmit(densityObject) {
            let oil = this.get('oil');
            set(oil, 'densities', densityObject);
            this.submit(oil);
        }
    }
});
