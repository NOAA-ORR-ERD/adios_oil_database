import { decamelize } from '@ember/string';
import JSONSerializer from '@ember-data/serializer/json';

export default JSONSerializer.extend({
  keyForAttribute(key) {
    return decamelize(key);
  }
});
