import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action, set } from "@ember/object";


export default class RangeValueInput extends Component {

    @tracked isShowingModal = false;
    @tracked valueObject;
    @tracked inputValue;

    constructor() {
        super(...arguments);

        this.valueObject = this.args.valueObject;

        if(this.valueObject){
            this.inputValue = this.deepGet(this.valueObject, this.args.valueName);
        }
        // form component ID - it needs to tether ember-modal-dialog to - replace spaces too
        this.componentId = this.args.valueTitle.replace(/\s+/g, '-').toLowerCase() + 
            this.args.sampleIndex;
    }

    deepGet(obj, path) {
        for (var i = 0, attrs = path.split('.'), len = attrs.length;
        i < len; i++) {
            try {
                obj = obj[attrs[i]];
            }
            catch(err) {
                return obj;  // undefined
            }
        }

        return obj;
    }

    deepSet(obj, path, value) {
        // protect against being something unexpected
        obj = typeof obj === 'object' ? obj : {};

        // split the path into and array if its not one already
        var keys = Array.isArray(path) ? path : path.split('.');
        var key;

        // loop over the path parts one at a time
        // but, dont iterate the last part,
        for (var i = 0; i < keys.length - 1; i++) {
            key = keys[i];

            if (!obj[key] && !Object.prototype.hasOwnProperty.call(obj, key)) {
                // if nothing exists for this key, make it an empty object or array
                // get the next key in the path, if its numeric, make this property
                // an empty array.  Otherwise, make it an empty object
                var nextKey = keys[i+1];
                var useArray = /^\+?(0|[1-9]\d*)$/.test(nextKey);
                obj[key] = useArray ? [] : {};
            }

            obj = obj[key];
        }

        // set our value
        // we need to use @ember/object:set() here because our oil is a tracked
        // property, and it is defined as old-style ember, not octane.
        key = keys[i];
        set(obj, key, value);

        return obj;
    }
    
    enteredValuesValid(entered) {
        if (!entered) { return false }

        if (!(entered.hasOwnProperty("min_value") ||
              entered.hasOwnProperty("max_value") ||
              entered.hasOwnProperty("value")))
        {
            return false;
        }

        return true;
    }

    get editable() {
        return this.args.editable;
    }

    @action
    openModalDialog(){
        this.isShowingModal = true;
    }

    @action
    closeModalDialog() {
        this.isShowingModal = false;
    }

    @action
    updateValue(enteredValue) {
        let newValue;
        if (this.enteredValuesValid(enteredValue)) {
            newValue = enteredValue;
        }
        else {
            // nothing entered - This happens when we have no values in the
            // dialog and then press OK.  We will view this as an intentional
            // nullification of the property.
            newValue = null;
        }    

        this.deepSet(this.valueObject, this.args.valueName, newValue);
        this.inputValue = newValue;

        console.log('setting this.valueObject...');
        this.valueObject = this.valueObject; // ember! - reset tracked object

        if (this.args.submit) {
            this.args.submit();
        }
        else {
            console.warn('No submit method for', this.args.valueName);
        }
    }
}
