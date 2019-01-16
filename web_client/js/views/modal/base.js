define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'text!templates/modal/base.html',
    'mousetrap'
], function($, _, Backbone, bs, ModalTemplate, Mousetrap) {
    'use strict';
    var baseModal = Backbone.View.extend({
        className: 'modal',
        name: 'default',
        title: 'Default Modal',
        body: '',
        size: 'reg',
        rendered_: false,
        buttons: '<button type="button" class="cancel" data-dismiss="modal">Cancel</button><button type="button" class="save">Save</button>',
        options: {
            backdrop: false,
            keyboard: false,
            show: true,
            remote: false
        },

        initialize: function(options) {
            if (options) {
                if (options.body) {
                    this.body = options.body;
                }

                if (options.name) {
                    this.name = options.name;
                }

                if (options.title) {
                    this.title = options.title;
                }

                if (options.size) {
                    this.size = options.size;
                }

                if (options.buttons) {
                    this.buttons = options.buttons;
                }
            }

            weboillib.router.on('route', this.close, this);
        },

        events: {
            'hide.bs.modal': 'close',
        },

        show: function() {
            this.$el.modal('show');
        },

        hide: function() {
            this.$el.modal('hide');
        },

        toggle: function() {
            this.$el.modal('toggle');
        },

        render: function(options) {
            if (_.isFunction(this.body)) {
                this.body = this.body();
            }

            var compiled = _.template(ModalTemplate,
                                      {size: this.size,
                                       title: this.title,
                                       body: this.body,
                                       buttons: this.buttons});
            this.$el.append(compiled);
            this.rendered_ = true;

            if (_.isObject(this.body)) {
                this.$el.find('.modal-body').html('').append(this.body);
            }

            $('body').append(this.$el);
            this.$el.modal(this.options);

            // Bind the 'enter' and 'esc' keyboard events to submit the
            // form modal in the same way as if a user clicked the save or
            // cancel buttons, respectively.
            Mousetrap.bind('enter', _.bind(this.submitByEnter, this));
            Mousetrap.bind('esc', _.bind(this.cancelByEsc, this));

            // Added mousetrap class to all of the input elements so that
            // enter will still fire even if an input field is focused
            // at the time.
            // Link to docs here: http://craig.is/killing/mice#api.bind.text-fields
            this.$('input').addClass('mousetrap');
            this.$('select').addClass('mousetrap');

            if (_.isUndefined(this.resizeEvent)) {
                this.resizeEvent = this.$('.modal-body').on('resize',
                                                            _.bind(this.windowResize, this));
            }
        },

        windowResize: function(e) {
            $(window).trigger('resize');
        },

        submitByEnter: function(e) {
            e.preventDefault();
            this.$(':focus').blur();
            this.$('.save').click();

            if (this.$('.next').length > 0) {
                this.$('.next').click();
            }
            else if (this.$('.finish').length > 0) {
                this.$('.finish').click();
            }
            else if (this.$('.cancel').length > 0 &&
                     this.$('.save').length === 0) {
                this.$('.cancel').click();
            }
        },

        cancelByEsc: function(e) {
            e.preventDefault();
            this.$('.cancel').click();

            if (this.$('.cancel').length === 0) {
                this.$('.close').click();
            }
        },

        updateTooltipWidth: function() {
            this.$('.slider .tooltip').each(function() {
                var chars = $(this).text().split('').length;
                var width = 0;

                if (chars <= 3) {
                    width = 40;
                }
                else if(chars === 4) {
                    width = chars * 10;
                }
                else {
                    width = chars * 9;
                }

                var margin = (width / 2) - parseInt(7, 10);

                $(this).css({
                    width: width + 'px',
                    marginLeft: '-' + margin + 'px'
                });
            });
        },

        close: function() {
            weboillib.router.off('route', this.close, this);
            Backbone.View.prototype.close.call(this);
        }
    });

    return baseModal;
});
