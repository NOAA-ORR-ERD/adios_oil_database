define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/default/help.html',
    'text!templates/default/help-tab.html',
    'model/help/help',
    'model/help/feedback'
], function($, _, Backbone,
            HelpTemplate, HelpTabTemplate, HelpModel, FeedbackModel) {
    'use strict';
    var helpView = Backbone.View.extend({
        className: 'help-content',
        ready: false,

        events: {
            'click .helpful a': 'logHelpful',
            'click .send': 'logResponse'
        },

        initialize: function(options) {
            _.defaults(options, {
                context: 'modal'
            });

            if (_.has(options, 'path')) {
                this.help = new HelpModel({id: options.path});
                this.help.fetch({
                    success: _.bind(function() {
                        this.ready = true;
                        this.render(options.context);
                        this.trigger('ready');
                    }, this)
                });
            }
        },

        render: function(context) {
            var compiled;

            if ($('<div>' + this.help.get('html') + '</div>').find('.document').length <= 1) {
                compiled = _.template(HelpTemplate, {
                    html: this.help.get('html')
                });
            }
            else {
                var tabs = this.getTabs(this.help.get('html'));
                var html = $('<div>' + this.help.get('html') + '</div>');

                html.find('.title').hide();
                html.find('.document:first').addClass('active');
                html.find('.document').addClass('tab-pane');

                compiled = _.template(HelpTabTemplate,
                                      {tabs: tabs,
                                       html: html.html()}
                                      );
            }

            this.$el.append(compiled);

            if (context === 'modal') {
                this.$el.addClass('alert alert-info alert-dismissable');
            }
            else if (context === 'view') {
                this.$('.title').hide();
                this.$('.close').remove();
            }
        },

        logHelpful: function(e) {
            var target;

            if (e.target.nodeName === 'SPAN') {
                target = e.target.parentElement;
            }
            else {
                target = e.target;
            }

            var ishelpful = $(target).data('helpful');

            this.$('.helpful a').removeClass('selected');
            this.$(target).addClass('selected');

            this.help.set('helpful', ishelpful);

            this.help.save(null, {
                success: _.bind(function() {
                    if (this.help.get('helpful') === false) {
                        this.showResponse();
                    }
                }, this)
            });
        },

        showResponse: function() {
            this.$('.response').show();
        },

        logResponse: function() {
            this.help.set('response', this.$('textarea').val());

            this.help.save(null, {
                success: _.bind(function() {
                    this.$('.helpful, .response').hide();
                    this.$('.thankyou').fadeIn();
                }, this)
            });
        },

        getTabs: function(html) {
            if (_.isUndefined(html)) { return '';}

            var tabs = '';
            html = $(html);
            var headers = html.find('.title');

            headers.each(function(i, el) {
                if (i === 0) {
                    tabs += '<li class="active"><a href="#' + $(el).parent().attr('id') + '" data-toggle="tab">' + $(el).text() + '</a></li>';
                }
                else {
                    tabs += '<li><a href="#' + $(el).parent().attr('id') + '" data-toggle="tab">' + $(el).text() + '</a></li>';
                }
            });

            return tabs;
        }
    });

    return helpView;
});
