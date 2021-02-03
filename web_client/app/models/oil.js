import Model, { attr } from '@ember-data/model';


export default class OilModel extends Model {
    // These attributes are used in the table columns of the search as well as
    // the full records
    @attr metadata;
    @attr status;
    @attr sub_samples;
    @attr extra_data;
}
