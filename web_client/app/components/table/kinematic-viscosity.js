import Component from '@ember/component';
import { set } from "@ember/object";

export default Component.extend({

    init(){
        this._super(...arguments);
    },
    
    actions: {
        onSubmit(kvisValue) {
            let oil = this.get('oil');
            set(oil, 'kvis', kvisValue);
            this.submit(oil);
        }
    }
});
