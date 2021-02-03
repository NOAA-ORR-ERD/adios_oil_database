import Model, { attr } from '@ember-data/model';

export default class LabelModel extends Model {
    @attr name;
    @attr product_types;
}
