define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/oil/oil_info.html',
    'model/oil'
], function($, _, Backbone,
            OilInfoTemplate, OilModel) {
    'use strict';
    var oilInfoView = Backbone.View.extend({
        className: 'oilInfoView',

        model: new OilModel(),

        events: {
        },

        initialize: function(model) {
            var oil = new OilModel(model);

            oil.fetch({
                success: function (oil) {
                    console.log('oil fetch success');
                    this.render(oil);
                }
            }, this);
        },

        render: function(model) {
            var compiled = _.template(OilInfoTemplate,
                                      {data: model});
            $('body').append(this.$el.append(compiled));
        },
    });

    return oilInfoView;
});
