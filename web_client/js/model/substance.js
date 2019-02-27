define([
    'underscore',
    'backbone',
    'model/base'
], function(_, Backbone, BaseModel) {
    'use strict';
    var Substance = BaseModel.extend({
        url: function() {
            return (weboildb.config.oil_api +
                    '/oil/?adios_oil_id=' +
                    this.get('adios_oil_id'));
        },

        parseTemperatures: function() {
            var flashPointK = this.get('flash_point_max_k');
            var pourPointK = this.get('pour_point_max_k');

            var flashPointC = flashPointK - 273.15;
            var flashPointF = (flashPointC * (9 / 5)) + 32;

            var pourPointC = pourPointK - 273.15;
            var pourPointF = (pourPointC * (9 / 5)) + 32;

            return {
                    'pour_point_max_c': pourPointC.toFixed(1),
                    'pour_point_max_f': pourPointF.toFixed(1),
                    'flash_point_max_c': flashPointC.toFixed(1),
                    'flash_point_max_f': flashPointF.toFixed(1)
                   };
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
        },

        parseCategories: function() {
            var cats = this.get('categories');
            var output = [];

            for (var c in cats) {
                output.push(cats[c].parent.name + ' - ' + cats[c].name);
            }

            return output;
        }
    });

    return Substance;
});
