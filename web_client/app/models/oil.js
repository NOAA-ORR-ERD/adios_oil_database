import Model, { attr } from '@ember-data/model';


export default class OilModel extends Model {
    // These attributes are used in the table columns of the search as well as
    // the full records
    @attr oil_id;
    @attr adios_data_model_version;
    @attr metadata;
    @attr status;
    @attr review_status;
    @attr permanent_warnings;
    @attr sub_samples;
    @attr extra_data;
}
