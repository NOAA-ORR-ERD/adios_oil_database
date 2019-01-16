define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/attributes/panel.html',
    'views/attributes/table'
], function($, _, Backbone, PanelTemplate, AttributesTable) {
    'use strict';
    var AttributesView = Backbone.View.extend({
        className: 'attributes',

        events: {
            'click .panel-heading': 'expand'
        },

        initialize: function(options) {
            if (!_.has(options, 'model')) { return null; }

            if (_.has(options, 'superModel')) {
                this.model = options.superModel;
            }
            else {
                this.model = options.model;
            }

            if (options.name) {
                this.name = options.name;
            }

            this.render();
        },

        render: function() {
            if (this.model) {
                this.$el.append(_.template(PanelTemplate, {
                    title: (this.name ? this.name : '')
                }));

                if (this.model.length > 0) {
                    this.model.forEach(_.bind(function(model) {
                        this.$('.panel-body:first')
                            .append(new AttributesView({name: model.get('obj_type') + ' | ' + model.get('name'), model: model}).$el);
                    }, this));
                }
                else {
                    this.$('.panel-body')
                        .append(new AttributesTable({model: this.model}).$el);
                }

                var submodels = _.keys(this.model.model);

                for (var key in submodels) {
                    var name = '';
                    if (this.model.get(submodels[key]) &&
                            this.model.get(submodels[key]).get('obj_type')) {
                        name = this.model
                                   .get(submodels[key])
                                   .get('obj_type') + ' | ' + this.model.get(submodels[key]).get('name');
                    }
                    else {
                        name = submodels[key];
                    }

                    this.$('.panel-body:first').append(new AttributesView({
                        model: this.model.get(submodels[key]),
                        name: name
                    }).$el);
                }
            }
        },

        expand: function(e) {
            this.$(e.currentTarget)
                .parents('.attributes:first')
                .find('.collapse:first')
                .collapse('toggle');
        }
    });

    return AttributesView;
});
