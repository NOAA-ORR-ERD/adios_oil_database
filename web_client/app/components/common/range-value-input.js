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
        let keys = Array.isArray(path) ? path : path.split('.');

        for (let i = 0, len = keys.length; i < len; i++) {
            try {
                obj = obj[keys[i]];
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

        let keys = Array.isArray(path) ? path : path.split('.');
        let key;

        // loop over the path parts one at a time, all but the last part
        for (var i = 0; i < keys.length - 1; i++) {
            key = keys[i];

            if (!obj[key] && !Object.prototype.hasOwnProperty.call(obj, key)) {
                // If nothing exists for this key, make it an empty object
                // or array, depending upon the next key in the path.
                // If it's numeric, make this property an empty array.
                // Otherwise, make it an empty object
                var nextKey = keys[i+1];
                var useArray = /^\+?(0|[1-9]\d*)$/.test(nextKey);
                obj[key] = useArray ? [] : {};
            }

            obj = obj[key];
        }

        // we need to use @ember/object:set() here because our oil is a tracked
        // property, and it is defined as old-style ember, not octane.
        key = keys[i];
        set(obj, key, value);

        return obj;
    }

    deepRemove(obj, path) {
        let keys = Array.isArray(path) ? path : path.split('.');

        if (keys.length >= 2) {
            let parent = this.deepGet(obj, keys.slice(0, -1));

            if (parent && parent.hasOwnProperty(keys.slice(-1)[0])) {
                delete parent[keys.slice(-1)[0]]
            }
        }

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
        if (this.enteredValuesValid(enteredValue)) {
            this.deepSet(this.valueObject, this.args.valueName, enteredValue);
            this.inputValue = enteredValue;
        }
        else {
            // nothing entered - This happens when we have no values in the
            // dialog and then press OK.  We will view this as an intentional
            // nullification of the property.
            this.deepRemove(this.valueObject, this.args.valueName);
            this.inputValue = null;
        }

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
