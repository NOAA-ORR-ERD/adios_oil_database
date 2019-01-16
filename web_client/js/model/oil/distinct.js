define([
    'jquery',
    'underscore',
    'backbone',
    'moment'
], function($, _, Backbone, moment) {
    'use strict';
    var oilDistinct = Backbone.Collection.extend({
        initialize: function(cb) {
            this.fetch({
                success: _.bind(this.setReady, this)
            });
        },
        
        url: function() {
            return weboillib.config.oil_api + '/distinct';
        },

        setReady: function() {
            this.ready = true;
            this.trigger('ready');
        },

        sync: function(method, model, options) {
            var oilDistinct = localStorage.getItem('oil_distinct');
            var success;

            if (!_.isNull(oilDistinct)) {
                oilDistinct = JSON.parse(oilDistinct);
                var ts = oilDistinct.ts;
                var now = moment().unix();

                if (now - ts < 86400) {
                    var data = oilDistinct.distinct;
                    options.success(data, 'success', null);
                }
                else {
                    success = options.success;

                    options.success = function(resp, status, xhr) {
                        oilDistinct.distinct = resp;
                        oilDistinct.ts = now;
                        localStorage.setItem('oil_distinct',
                                             JSON.stringify(oilDistinct));
                        success(resp, status, xhr);
                    };

                    Backbone.sync(method, model, options);
                }
            }
            else {
                success = options.success;

                options.success = function(resp, status, xhr) {
                    var now = moment().unix();
                    var oilDistinct = {};
                    oilDistinct.distinct = resp;
                    oilDistinct.ts = now;
                    localStorage.setItem('oil_distinct',
                                         JSON.stringify(oilDistinct));
                    success(resp, status, xhr);
                };

                Backbone.sync(method, model, options);
            }
        }
    });

    return oilDistinct;
});
