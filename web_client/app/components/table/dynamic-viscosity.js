import Component from '@ember/component';
import { set } from "@ember/object";

export default Component.extend({

    init(){
        this._super(...arguments);
    },
    
    actions: {
        onSubmit(dvisValue) {
            let oil = this.get('oil');
            set(oil, 'dvis', dvisValue);
            this.submit(oil);
        }
    }
});
