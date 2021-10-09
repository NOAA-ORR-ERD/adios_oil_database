import Component from '@glimmer/component';
import { set } from "@ember/object";


export default class BaseComponent extends Component {
    // This is where we can put basic functionality that we will expect most
    // of our components to need.

    deepGet(obj, path) {
        if (!path) {
            return obj;  // nothing to deepget
        }

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

}
