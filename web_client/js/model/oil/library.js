define([
    'jquery',
    'underscore',
    'backbone',
    'fuse',
    'moment'
], function($, _, Backbone, Fuse, moment) {
    'use strict';
    var oilLib = Backbone.Collection.extend({
        ready: false,
        loaded: false,
        sortAttr: 'name',
        sortDir: 1,

        initialize: function() {
            if (!this.loaded) {
                this.fetch({
                    success: _.bind(this.setReady, this)
                });
                this.loaded = true;
            }
        },

        url: function() {
            return weboillib.config.oil_api + '/oil';
        },

        fetchOil: function(id, cb) {
            var Oil = Backbone.Model.extend({
                urlRoot: this.url
            });
            var oil = new Oil({id: id});

            oil.fetch({
                success: cb
            });
        },

        convertValuesToLogScale: function(arr) {
            return [Math.pow(10, arr[0]), Math.pow(10, arr[1])];
        },

        filterCollection : function(arr, options) {
            var results;

            if (options.type === 'api') {
                results = this.filter(function(model) {
                    if (model.attributes[options.type] >= arr[0] &&
                            model.attributes[options.type] <= arr[1]) {
                        return true;
                    }
                    else {
                        return false;
                    }
                });
            }
            else if (options.type === 'viscosity') {
                var logArray = this.convertValuesToLogScale(arr);

                results = this.filter(function(model) {
                    // Converting the viscosity values from m^2/s to cSt
                    var viscosityInCst = model.attributes[options.type] * 1000000;

                    if (logArray[0] === 1) {
                        logArray[0] = 0;
                    }

                    if (viscosityInCst >= logArray[0] && viscosityInCst <= logArray[1]) {
                        return true;
                    }
                    else {
                        return false;
                    }
                });
            }
            else if (options.type === 'pour_point') {
                results = this.filter(function(model) {
                    if (model.attributes[options.type][0] > arr[1] ||
                            model.attributes[options.type][1] < arr[0]) {
                        return false;
                    }
                    else {
                        return true;
                    }
                });
            }
            else if (options.type === 'categories') {
                var str = arr.parent + '-' + arr.child;

                results = this.filter(function(model) {
                    return _.indexOf(model.attributes.categories, str) !== -1;
                });
            }

            return new Backbone.Collection(results);
        },

        search: function(obj) {
            this.models = this.originalModels;
            var categoryCollection = this;
            var apiCollection = this.filterCollection(obj.api, {type: 'api'});
            var pour_pointCollection = this.filterCollection(obj.pour_point, {type: 'pour_point'});

            if (obj.text.length > 1) {
                var options = {keys: ['attributes.name',
                                      'attributes.location',
                                      'attributes.categories_str',
                                      'attributes.synonyms'],
                               threshold: 0.3};

                var f = new Fuse(this.models, options);
                var result = f.search(obj.text);

                this.models = result;
            }

            if (obj.category.child !== '' && obj.category.child !== 'All') {
                categoryCollection = this.filterCollection(obj.category, {type: 'categories'});
            }

            this.models = _.intersection(this.models,
                                         pour_pointCollection.models,
                                         apiCollection.models,
                                         categoryCollection.models);
            this.length = this.models.length;

            return this;
        },

        comparator: function(a, b) {
            a = a.get(this.sortAttr);
            b = b.get(this.sortAttr);

            if (a === b) { return 0; }

            if (this.sortDir === 1) {
                return a > b ? 1 : -1;
            }
            else {
                return a < b ? 1 : -1;
            }
        },

        setReady: function() {
            this.ready = true;
            this.trigger('ready');
            this.loaded = true;
            this.originalModels = this.models;
        },

        sortOils: function(attr) {
            this.sortAttr = attr;
            this.sort();
        },

        sync: function(method, model, options) {
            var oilCache = localStorage.getItem('oil_cache');
            var success = options.success;

            if (!_.isNull(oilCache) && oilCache !== 'null') {
                oilCache = JSON.parse(oilCache);
                var ts = oilCache.ts;
                var now = moment().unix();

                if (now - ts < 86400) {
                    var data = oilCache.oils;
                    setTimeout(function() {
                        options.success(data, 'success', null);
                    }, 500);
                }
                else {
                    options.success = function(resp, status, xhr) {
                        var oilCache = {};
                        oilCache.oils = resp;
                        oilCache.ts = now;
                        localStorage.setItem('oil_cache',
                                             JSON.stringify(oilCache));
                        success(resp, status, xhr);
                    };

                    Backbone.sync(method, model, options);
                }
            }
            else {
                options.success = function(resp, status, xhr) {
                    var now = moment().unix();
                    var oilCache = {};

                    oilCache.oils = resp;
                    oilCache.ts = now;

                    localStorage.setItem('oil_cache',
                                         JSON.stringify(oilCache));
                    success(resp, status, xhr);
                };

                Backbone.sync(method, model, options);
            }

        }
    });

    return oilLib;
});
