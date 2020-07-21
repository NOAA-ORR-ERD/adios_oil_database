import { underscore } from '@ember/string';
import JSONAPISerializer from 'ember-data/serializers/json-api';

export default JSONAPISerializer.extend({
  primaryKey: '_id',

  keyForAttribute(attr) {
      return underscore(attr);
  }
});
