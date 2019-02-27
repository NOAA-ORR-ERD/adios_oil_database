define([
    'jquery',
    'underscore',
    'backbone',
    'chosen',
    'text!templates/default/faq.html',
    'model/help/help',
    'views/faq/default',
    'views/faq/single',
    'collection/help',
    'jqueryui/widgets/autocomplete'
], function($, _, Backbone, chosen,
            FAQTemplate, HelpModel, DefaultView, SingleView, HelpCollection) {
    'use strict';
	var faqView = Backbone.View.extend({
        className: 'page faq',

        events: function() {
            return _.defaults({
                'keyup input': 'update',
                'click .back': 'back',
                'click .topic': 'specificHelp'
            });
        },

        initialize: function(options) {
            this.seed();
            this.on('ready', this.parseHelp);
            this.fetchQuestions();

            if (!_.isUndefined(options.topic)) {
                this.cid = options.topic;
            }
        },

        render: function() {
            var compiled = _.template(FAQTemplate, {});
            $('.faqspace').append(this.$el.append(compiled));

            if (this.cid) {
                var title = decodeURI(this.cid);
                this.specificHelp({}, title);
            }
            else {
                this.defaultView = new DefaultView({topics: this.parsedData});
            }
        },

        update: function(e, str) {
            var term = this.$('.chosen-select').val();
            if (str){
                term = str;
            }

            this.topicArray = this.collection.search(term);
            var obj = this.getData(this.topicArray);
            var titles = [];

            for (var i in obj) {
                titles.push(obj[i].title);
            }

            var autocompleteConfig = {
                source: function(req, res) {
                    res(titles);
                },
                select: _.bind(function(e, ui) {
                    if (!_.isUndefined(e)) {
                        this.update({which: 13}, ui.item.value);
                    }
                    $('.chosen-select').autocomplete('close');
                }, this)
             };

            this.$('#helpquery').autocomplete(autocompleteConfig);

            if (e.which === 13) {
                this.specificHelp(null, term);
                $('.chosen-select').autocomplete('close');
            }

            this.trigger('updated');
        },

        seed: function() {
            $('.faqspace').remove();
            $('body').append('<div class="faqspace"></div>');
        },

        getData: function(models) {
            var data = {};
            if (_.isUndefined(models)) {
                models = this.body.models;
            }

            for (var i in models) {
                if (_.isObject(models[i])) {
                    var helpTopicBody = $('<div>' + models[i].get('html') + '</div>');
                    var helpTitle = helpTopicBody.find('h1:first').text();

                    helpTopicBody.find('h1:first').remove();

                    var helpContent = helpTopicBody.html();
                    var path = models[i].get('path');
                    var excerpt = models[i].makeExcerpt();
                    var keywords = models[i].get('keywords');
                    var id = models[i].cid;

                    if (helpTitle !== '' && excerpt !== '') {
                        data[helpTitle] = {id: id,
                                           title: helpTitle,
                                           path: path,
                                           content: helpContent,
                                           excerpt: excerpt,
                                           keywords: keywords};
                    }
                }
            }
            return data;
        },

        parseHelp: function() {
            this.parsedData = this.getData();
            this.render();
        },

        fetchQuestions: function() {
            this.collection = new HelpCollection();
            this.collection.fetch({
                success: _.bind(function(model) {
                    this.body = model;
                    this.trigger('ready');
                }, this)
            });
        },

        specificHelp: function(e, title) {
            var data = this.parsedData;
            var target;
            var compiled;
            var subtemplate;

            if (_.isNull(e) || _.isEmpty(e)) {
                target = data[title].id;
            }
            else if (_.isUndefined(this.$(e.target).data().cid)) {
                target = $(this.$(e.target).siblings('h4')[0]).data().cid;
            }
            else {
                target = this.$(e.target).data().cid;
            }

            for (var i in data) {
                if (data[i].id === target) {
                    this.singleHelp = new SingleView({topic: data[i]});
                    target = data[i].id;
                    break;
                }
            }

            var encodedUrl = encodeURI(target);
            weboildb.router.navigate('faq/' + encodedUrl);
        },

        back: function() {
            this.restoreDefault();
            this.$('.chosen-select').val('');
            //weboildb.router.navigate('faq', {trigger: true});
        },

        restoreDefault: function(clear) {
            this.defaultView = new DefaultView({topics: this.parsedData});
            weboildb.router.navigate('faq');
        }
    });

    return faqView;
});
