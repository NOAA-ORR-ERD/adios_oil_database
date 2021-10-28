import { helper } from '@ember/component/helper';

// There are times when an object attribute does not exist, and we try to
// use it by passing it into a component.  When this happens, the argument
// passed into the component is detached from our record structure,
// making it impossible to edit that part of our record structure.
//
// Most of the time, this problem can be solved by setting initial conditions
// inside the constructor of the javascript class for our component.
// But sometimes it would be more convenient if we could set the inital
// condition inside the template.
//
// So this helper is intended to do just that.
export function setAttrIfNone([obj,
                               attr,
                               defaultValue,
                               ...rest]) {  // eslint-disable-line no-unused-vars
    if (!obj[attr]) {
        obj[attr] = defaultValue;
    }
    
    return obj;
}

export default helper(setAttrIfNone);
