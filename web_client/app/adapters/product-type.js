import ApplicationAdapter from './application';
import { dasherize } from '@ember/string';
import { pluralize } from 'ember-inflector';


export default class ProductTypeAdapter extends ApplicationAdapter {
    pathForType(type) {
        return pluralize(dasherize(type));
    }
}
