define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/default/overview.html'
], function($, _, Backbone, FAQTemplate){
    'use strict';
	var overviewView = Backbone.View.extend({
        className: 'page overview',

        events: {
            'click .resume': 'resume',
            'click .build': 'build',
            'click .load': 'load',
        },

        initialize: function(){
            this.render();
        },

        render: function(){
            var compiled = _.template(FAQTemplate, {});
            $('body').append(this.$el.append(compiled));
        }
    });

    return overviewView;
});