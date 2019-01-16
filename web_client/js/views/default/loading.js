define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {
    'use strict';
    var loadingView = Backbone.View.extend({
        className: 'app-state loading',
        initialize: function(options) {
            this.render();
        },

        render: function() {
            if ($('.app-state.loading').length === 0 && $('.loading-modal').length === 0) {
                var text = 'Loading';

                this.$el.append('<div class="spinner"></div>' + text);
                $('body').append(this.$el);
            }
        }
    });

    return loadingView;
});
