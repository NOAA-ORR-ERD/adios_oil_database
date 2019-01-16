define([
    'jquery',
    'underscore',
    'backbone',
    'model/oil/library',
    'text!templates/oil/table.html'
], function($, _, Backbone, OilLib, OilTableTemplate){
    'use strict';
    var oilTableView = Backbone.View.extend({
        id: 'tableContainer',
        ready: false,
        events: {
            'click th': 'headerClick',
            'click td': 'oilSelect',
            'click .backOil': 'goBack',
            'click .oilInfo': 'viewSpecificOil',
            'dblclick td': 'viewSpecificOil'
        },
        sortUpIcon: '&#9650;',
        sortDnIcon: '&#9660;',
        activeIcon: null,

        initialize: function(elementModel) {
            this.oilLib = new OilLib();
            this.model = elementModel;
            this.oilLib.once('ready', this.sortTable, this);
            this.oilLib.once('ready', this.setReady, this);
            this.on('sort', this.sortTable);
        },

        setReady: function() {
            this.ready = true;
            this.trigger('ready');
        },

        sortTable: function() {
            var compiled = _.template(OilTableTemplate, {
            	data: this.oilLib
            });
            this.$el.html(compiled);

            this.set_quality_index_colors(this.$el);

            var substance = !_.isEmpty(this.model) ? this.model.get('substance') : null;
            if (substance && substance.get('adios_oil_id')) {
                this.$('tr[data-id="' + substance.get('adios_oil_id') + '"]').addClass('select');
            }

            this.$('tr[data-generic="true"]').addClass('generic');
            var generics = this.$('.generic td:first-child');

            this.updateCaret();
            this.processCategory();
            this.trigger('renderTable');
        },

        updateCaret: function() {
             if (this.oilLib.sortDir === 1) {
                this.activeIcon = this.sortUpIcon;
            } else {
                this.activeIcon = this.sortDnIcon;
            }
            this.$('.' + this.oilLib.sortAttr + ' span').html(this.activeIcon);
        },

        processCategory: function() {
            var categoryLabels = this.$('.label-warning');
            for (var i = 0; i < categoryLabels.length; i++) {
                var htmlStr = this.$(categoryLabels[i]).html();
                this.$(categoryLabels[i]).html(htmlStr.replace('Crude-', 'Crude: ').replace('Refined-', '').replace('Other-', ''));
            }
        },

        render: function() {
            this.trigger('sort');
        },

        set_quality_index_colors: function(table_container) {
            var qi_idx = table_container.find('th.quality_index').index() + 1;

            table_container.find('tr td:nth-child(' + qi_idx + ')')
            .each(function() {
            	var cell = this;
                var quality_index = parseFloat(cell.textContent);

                if (quality_index <= 50.0) {
                    $(cell).addClass('danger');
                }
                else if (quality_index <= 70.0) {
                    $(cell).addClass('warning');
                }
                else {
                    $(cell).addClass('success');
                }
            });
        },

        headerClick: function(e){
            var ns = e.target.className,
                cs = this.oilLib.sortAttr;

            if (ns === cs){
                this.oilLib.sortDir *= -1;
            } else {
                this.oilLib.sortDir = 1;
            }

            $(e.currentTarget).closest('thead').find('span').empty();

            this.oilLib.sortOils(ns);
            this.trigger('sort');
        }

    });
    return oilTableView;
});