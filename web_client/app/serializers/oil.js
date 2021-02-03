import JSONAPISerializer from '@ember-data/serializer/json-api';
import { underscore } from '@ember/string';

export default class OilSerializer extends JSONAPISerializer {
    primaryKey = '_id';

    keyForAttribute(attr) {
        return underscore(attr);
    }
}
