import Model, { attr } from '@ember-data/model';

export default class CapabilityModel extends Model {
    @attr can_modify_db;
  }
