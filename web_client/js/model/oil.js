define([
    'underscore',
    'backbone',
    'model/base'
], function(_, Backbone, BaseModel) {
    'use strict';
    var Oil = BaseModel.extend({
        idAttribute: "adios_oil_id",

        url: function() {
            return (weboildb.config.oil_api + '/oil/' +
                    this.get('adios_oil_id'));
        },

        validate: function(attrs, options) {
            // if (_.isUndefined(attrs.bullwinkle_fraction)){
            //     return 'Stable emulsion fraction must be defined!';
            // }

            // if (_.isUndefined(attrs.emulsion_water_fraction_max)){
            //     return 'Emulsion constant must be defined!';
            // }
            
            // if (!_.isNumber(attrs.bullwinkle_fraction) || (attrs.bullwinkle_fraction < 0 || attrs.bullwinkle_fraction > 1)){
            //     return 'Stable emulsion fraction must be a number between zero and one!';
            // }

            // if (!_.isNumber(attrs.emulsion_water_fraction_max) || (attrs.emulsion_water_fraction_max < 0 || attrs.emulsion_water_fraction_max > 1)){
            //     return 'Emulsion constant must be a number between zero and one!';
            // }
        }
    });

    return Oil;
});
