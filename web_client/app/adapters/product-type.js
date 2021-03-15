import ApplicationAdapter from './application';
import { dasherize } from '@ember/string';
import { pluralize } from 'ember-inflector';


export default class ProductTypeAdapter extends ApplicationAdapter {
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    };

    ajax(url, method, options) {
        if (options === undefined) { options = {}; }

        options.crossDomain = true;
        options.xhrFields = { withCredentials: true };

        return super.ajax(url, method, options);
    }

    buildURL(type, id, record) {
        //call the default buildURL and then append a slash
        return super.buildURL(type, id, record) + '/';
    }

    pathForType(type) {
        return pluralize(dasherize(type));
    }
}
