define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/attributes/row.html'
], function($, _, Backbone, RowTemplate){
    var attributesTable = Backbone.View.extend({
        tagName: 'table',
        className: 'table table-condensed table-striped',

        events: {
            'change input,select': 'update',
        },

        initialize: function(options) {
            if (!_.has(options, 'model')) { return null; }

            this.model = options.model;
            this.render();
        },

        render: function() {
            var ignore = ['obj_type',
                          'id',
                          'map',
                          'outputter',
                          'spills',
                          'weatherers',
                          'environment',
                          'json_', 
                          'outputters',
                          'movers'];

            if (this.title) {
                this.$el.append('<h4>' + this.title + '</h4>');
            }

            for (var attr in this.model.attributes){
                if (ignore.indexOf(attr) === -1 &&
                        !_.isObject(this.model.attributes[attr]) ||
                        ignore.indexOf(attr) === -1 &&
                        _.isArray(this.model.attributes[attr])) {
                    var type = 'text';
                    var value = this.model.attributes[attr];

                    if (_.isNumber(value)) {
                        type = 'number';
                    }
                    else if (_.isBoolean(value)) {
                        type = 'boolean';
                    }
                    else if (_.isArray(value)) {
                        type = 'array';
                    }

                    this.$el.append(_.template(RowTemplate,
                                               {name: attr,
                                                value: value,
                                                type: type}));
                }
            }
        },

        update: function(e) {
            var attribute = this.$(e.currentTarget).data('attribute');
            var value = this.$(e.currentTarget).val();
            var type = this.$(e.currentTarget).attr('type');

            if (type === 'number') {
                value = parseFloat(value);
            }
            else if (type === 'array') {
                value = JSON.parse('[' + value + ']');
            }

            this.model.set(attribute, value, {silent: true});
        }
    });

    return attributesTable;
});
