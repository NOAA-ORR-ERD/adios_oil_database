define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/default/index.html',
    'views/form/oil/library'
], function($, _, Backbone,
            IndexTemplate, OilLibraryView) {
    'use strict';
    var indexView = Backbone.View.extend({
        className: 'page home',

        events: {'click .query': 'query',
                 'click .oillib': 'oillib',
                 'click .doc': 'doc'
        },

        initialize: function() {
            this.render();
        },

        render: function() {
            var compiled = _.template(IndexTemplate);
            $('body').append(this.$el.append(compiled));
        },

        query: function(event) {
            event.preventDefault();
            weboillib.router.navigate('query', true);
        },

        oillib: function(e) {
            var oillib = new OilLibraryView({});
            oillib.on('save wizardclose', _.bind(function() {
                oillib.close();
            }, this));
            oillib.render();
            oillib.$el.addClass('viewer');
        },

        doc: function(event) {
            event.preventDefault();
            window.open("doc/");
        },

        close: function() {
            Backbone.View.prototype.close.call(this);
        }
    });

    return indexView;
});
