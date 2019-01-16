define([
    'jquery',
    'underscore',
    'backbone',
    'chosen',
    'text!templates/faq/default.html'
], function($, _, Backbone, chosen, DefaultTemplate) {
    'use strict';
    var faqDefaultView = Backbone.View.extend({
        className: 'helpcontent',
        id: 'support',

        events: function() {
            return _.defaults({

            });
        },

        initialize: function(options) {
            this.topics = options.topics;
            this.render();
        },

        render: function() {
            $('#support').html('');
            var compiled = _.template(DefaultTemplate, {topics: this.topics});
            $('#support').html(this.$el.append(compiled));
        }

    });

    return faqDefaultView;
});