import Model, { attr } from '@ember-data/model';


export default class ConfigModel extends Model {
    @attr comments;
    @attr webApi;
    @attr ignoreWarnings;
    @attr template;
}
