import JSONSerializer from '@ember-data/serializer/json';
import { decamelize } from '@ember/string';

export default class ApplicationSerializer extends JSONSerializer {
  keyForAttribute(key) {
    return decamelize(key);
  }
}
