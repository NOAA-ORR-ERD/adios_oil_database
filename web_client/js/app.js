// basic controller to configure and setup the app
define([
    'jquery',
    'underscore',
    'backbone',
    'moment',
    'sweetalert',
    'text!../config.json',
    'router',
    'model/session',
    'model/user_prefs',
    'views/default/loading'
], function($, _, Backbone, moment, swal,
            config, Router, SessionModel, UserPrefs,
            LoadingView) {
    'use strict';
    var app = {
        obj_ref: {},

        initialize: function() {
            this.ajaxSuppressCaching();

            this.configure();
            this.capabilities();

            this.config.date_format.half_hour_times = this.generateHalfHourTimesArray();
            this.config.date_format.time_step = 30;

            this.monitor = {};
            this.monitor.requests = [];

            swal.setDefaults({'allowOutsideClick': false});

            $.ajaxPrefilter(_.bind(function(options, originalOptions, jqxhr) {
                if (options.url.indexOf('http://') === -1 &&
                        options.url.indexOf('https://') === -1) {
                    options.url = weboildb.config.oil_api + options.url;
                    // add a little cache busting so IE doesn't cache everything...
                    options.url += '?' + (Math.random()*10000000000000000);
                }
                else {
                    // If this request is going somewhere other than the
                    // oil_database_api, we shouldn't enforce credentials.
                    delete options.xhrFields.withCredentials;
                }

                // monitor interation to check the status of active ajax calls.
                this.monitor.requests.push(jqxhr);

                if (_.isUndefined(this.monitor.interval)) {
                    this.monitor.start_time = moment().valueOf();

                    this.monitor.interval = setInterval(_.bind(function() {
                        var loading;

                        if (this.monitor.requests.length > 0) {
                            this.monitor.requests = this.monitor.requests.filter(function(req) {
                                if (req.status !== undefined) {
                                    if (req.status !== 404 && req.status.toString().match(/5\d\d|4\d\d/)) {
                                        if ($('.modal').length === 0) {
                                            swal({
                                                title: 'Application Error!',
                                                text: 'An error in the application has occured.<br/><br/><code>' + req.responseText + '</code>',
                                                type: 'error',
                                                confirmButtonText: 'Ok'
                                            });
                                        }
                                    }
                                }
                                return req.status === undefined;
                            });
                        }
                        else {
                            clearInterval(this.monitor);
                            this.monitor.interval = undefined;
                            this.monitor.start_time = moment().valueOf();
                        }

                        // check if we need to display a loading message.
                        if (moment().valueOf() - this.monitor.start_time > 300) {
                            if (_.isUndefined(this.monitor.loading)) {
                                this.monitor.loading = new LoadingView();
                            }
                        }
                        else {
                            if (!_.isUndefined(this.monitor.loading)) {
                                this.monitor.loading.close();
                                this.monitor.loading = undefined;
                            }
                        }
                    }, this), 500);
                }
            }, this));

            this.router = new Router();

            // TODO: get the session api working on the oil api server
            //new SessionModel(function() {
            //    Backbone.history.start();
            //    weboildb.router.navigate('overview', true);
            //});

            Backbone.history.start();
        },

        configure: function() {
            // TODO: is it possible to move this config step out of the app?
            //       maybe using inheritance w/ base view?

            this.config = this.getConfig();

            // Use Django-style templates semantics with Underscore's _.template.
            _.templateSettings = {
                // {{- variable_name }} -- Escapes unsafe output (e.g. user
                // input) for security.
                escape: /\{\{-(.+?)\}\}/g,

                // {{ variable_name }} -- Does not escape output.
                interpolate: /\{\{(.+?)\}\}/g,

                // {{ javascript }}
                evaluate: /\{\%(.+?)\%\}/g
            };

            Backbone.View.prototype.close = function() {
                this.remove();
                this.unbind();

                if (this.onClose) {
                    this.onClose();
                }
            };

            Backbone.Model.prototype.close = function() {
                this.clear();
                this.unbind();

                if (this.onClose) {
                    this.onClose();
                }
            };

            this.implement_fancy_tree();

            // use this transport for "binary" data type
            $.ajaxTransport("+binary", function(options, originalOptions, jqXHR) {
                var callback,
                    xhrSuccessStatus = {
                        // file protocol always yields status code 0,
                        // assume 200
                        0: 200,
                        // Support: IE9
                        // #1450: sometimes IE returns 1223
                        // when it should be 204
                        1223: 204
                    };

                // check for conditions and support for blob / arraybuffer
                // response type
                if (window.FormData &&
                        ((options.dataType && (options.dataType === 'binary')) ||
                         (options.data &&
                          ((window.ArrayBuffer && options.data instanceof ArrayBuffer) ||
                           (window.Blob && options.data instanceof Blob))
                          ))
                    )
                {
                    var xhrCallbacks = {}, xhrId=0;

                    return {
                        // create new XMLHttpRequest
                        send: function(headers, complete) {
                            // setup all variables
                            var i, xhr = options.xhr(), id = ++xhrId;

                            xhr.open(options.type, options.url, options.async,
                                     options.username, options.password);

                            if (options.xhrFields) {
                                for (i in options.xhrFields) {
                                    xhr[i] = options.xhrFields[i];
                                }
                            }

                            // Override mime type if needed
                            if (options.mimeType && xhr.overrideMimeType) {
                                xhr.overrideMimeType(options.mimeType);
                            }

                            // X-Requested-With header
                            // For cross-domain requests, seeing as conditions
                            // for a preflight are akin to a jigsaw puzzle,
                            // we simply never set it to be sure.
                            // (it can always be set on a per-request basis
                            // or even using ajaxSetup)
                            // For same-domain requests, won't change header
                            // if already provided.
                            if (!options.crossDomain &&
                                    !headers["X-Requested-With"]) {
                                headers["X-Requested-With"] = "XMLHttpRequest";
                            }

                            // Set headers
                            for ( i in headers ) {
                                xhr.setRequestHeader( i, headers[ i ] );
                            }

                            xhr.responseType = "arraybuffer";

                            // Callback
                            callback = function(type) {
                                return function() {
                                    if (callback) {
                                        delete xhrCallbacks[id];
                                        callback = xhr.onload = xhr.onerror = null;

                                        if (type === "abort") {
                                            xhr.abort();
                                        }
                                        else if (type === "error") {
                                            complete(
                                                // file: protocol always yields
                                                // status 0;
                                                xhr.status, xhr.statusText
                                            );
                                        }
                                        else {
                                            complete(
                                                xhrSuccessStatus[ xhr.status ] || xhr.status,
                                                xhr.statusText,
                                                // Support: IE9
                                                // Accessing binary-data responseText throws an exception
                                                {binary: xhr.response},
                                                xhr.getAllResponseHeaders()
                                            );
                                        }
                                    }
                                };
                            };

                            // Listen to events
                            xhr.onload = callback();
                            xhr.onerror = callback("error");

                            // Create the abort callback
                            callback = xhrCallbacks[id] = callback("abort");

                            try {
                                xhr.send(options.hasContent && options.data || null);
                            }
                            catch (e) {
                                // Only rethrow if this hasn't been notified
                                // as an error yet
                                if (callback) {
                                    throw e;
                                }
                            }
                        },

                        abort: function() {
                            if (callback) {
                                callback();
                            }
                        }
                    };
                }
            });
        },

        implement_fancy_tree: function() {
            //
            // Convert the model's or collection's attributes into the format needed by
            // fancy tree for rendering in a view
            // @return {Object} formated json object for fancy tree
            //
            Backbone.Model.prototype.toTree = function(use_attrs) {
                var attrs = _.clone(this.attributes);
                var tree = [];
                var children = [];

                if (_.isUndefined(use_attrs)) {
                    use_attrs = true;
                }

                for (var key in attrs) {
                    var el = attrs[key];
                    // flat attribute just set the index and value
                    // on the tree. Should map to the objects edit form.
                    if (!_.isObject(el) && use_attrs === true) {
                        tree.push({title: key + ': ' + el,
                                   key: el,
                                   obj_type: attrs.obj_type,
                                   action: 'edit',
                                   object: this});
                    }
                    else if (_.isObject(el) &&
                             !_.isArray(el) &&
                             !_.isUndefined(el.obj_type)) {
                        // child collection/array of children or
                        // single child object
                        if (_.has(el, 'toTree')) {
                            children.push({title: key + ':',
                                           children: el.toTree(),
                                           expanded: true,
                                           obj_type: el.get('obj_type'),
                                           action: 'new'});
                        }
                    }
                    else if (_.isArray(el)) {
                        var arrayOfStrings = [];

                        for (var i = 0; i < el.length; i++) {
                            var arrayString = '[' + el[i] + ']';
                            var arrayObj = {title: arrayString};
                            arrayOfStrings.push(arrayObj);
                        }

                        if (el.length > 0) {
                            children.push({title: key + ': [...]',
                                           expanded: false,
                                           children: arrayOfStrings});
                        }
                        else {
                            children.push({title: key + ': []'});
                        }
                    }
                }

                tree = tree.concat(children);
                return tree;
            };

            Backbone.Model.prototype.toDebugTree = function() {
                var attrs = _.clone(this.attributes);
                var tree = [];
                var children = [];

                for (var key in attrs) {
                    var el = attrs[key];

                    // flat attribute just set the index and value
                    // on the tree. Should map to the objects edit form.
                    if (!_.isObject(el)) {
                        tree.push({title: key + ': ' + el,
                                   key: el,
                                   obj_type: attrs.obj_type,
                                   action: 'edit',
                                   object: this});
                        
                    }
                    else if (_.isObject(el) &&
                             !_.isArray(el) &&
                             el.toDebugTree) {
                        // child collection/array of children or
                        // single child object
                        children.push({title: key + ':',
                                       children: el.toDebugTree(),
                                       expanded: true,
                                       obj_type: el.get('obj_type'),
                                       action: 'new'});
                    }
                    else if (_.isArray(el)) {
                        var arrayOfStrings = [];

                        for (var i = 0; i < el.length; i++) {
                            var arrayString = '[' + el[i] + ']';
                            var arrayObj = {title: arrayString};
                            arrayOfStrings.push(arrayObj);
                        }
                        if (el.length > 0) {
                            children.push({title: key + ': [...]',
                                           expanded: false,
                                           children: arrayOfStrings});
                        }
                        else {
                            children.push({title: key + ': []'});
                        }
                    }
                }

                tree = tree.concat(children);
                return tree;
            };

            Backbone.Collection.prototype.toTree = function(name) {
                var models = _.clone(this.models);
                var tree = [];

                for (var model in models) {
                    var el = models[model];
                    tree.push({title: el.get('obj_type').split('.').pop(),
                               children: el.toTree(),
                               action: 'edit',
                               object: el,
                               expanded: true});
                }

                return tree;
            };

            Backbone.Collection.prototype.toDebugTree = function() {
                var models = _.clone(this.models);
                var tree = [];

                for (var model in models) {
                    var el = models[model];
                    tree.push({title: el.get('obj_type').split('.').pop(),
                               children: el.toDebugTree(),
                               action: 'edit',
                               object: el,
                               expanded: true});
                }

                return tree;
            };            
        },

        capabilities: function(){
            var thisApp = this;

            $.get(this.config.oil_api + '/capabilities')
            .done(function(result) {
                // We are just trying to figure out whether our API server
                // supports persistent uploads.  If we succeed here at all,
                // then persistent uploads are indeed supported
                Object.assign(thisApp.config, result);
            });
        },

        ajaxSuppressCaching: function() {
            // Ask jQuery to add a cache-buster to AJAX requests, so that
            // IE's aggressive caching doesn't break everything.
            $.ajaxSetup({
                xhrFields: {
                    withCredentials: true
                }
            });
        },

        generateHalfHourTimesArray: function() {
            var times = [];

            for (var i = 0; i < 24; i++) {
                times.push(i + ":00");
                times.push(i + ":30");
            }

            return times;
        },

        getForm: function(obj_type) {
            // right now we have no forms to get.  We will add them as needed.
            var map = {
                // 'gnome.model.Model': 'views/form/model',
            };

            return map[obj_type];
        },

        hasModel: function() {
            if (_.has(weboildb, 'model') &&
                    !_.isUndefined(weboildb.model) &&
                    _.isObject(weboildb.model) &&
                    !_.isUndefined(weboildb.model.get('id')))
            {
                return true;
            }
            return false;
        },

        getConfig: function() {
            return  JSON.parse(config);
        },

        validModel: function() {
            if (weboildb.hasModel()) {
                if (weboildb.model.isValid()) {
                    return true;
                }
            }
            return false;
        },

        invokeSaveAsDialog: function(file, fileName) {
            if (!file) {
                throw 'Blob object is required.';
            }

            if (!file.type) {
                try {
                    file.type = 'video/webm';
                } catch (e) {}
            }

            var fileExtension = (file.type || 'video/webm').split('/')[1];

            if (fileName && fileName.indexOf('.') !== -1) {
                var splitted = fileName.split('.');
                fileName = splitted[0];
                fileExtension = splitted[1];
            }

            var fileFullName = (fileName || (Math.round(Math.random() * 9999999999) + 888888888)) + '.' + fileExtension;

            if (typeof navigator.msSaveOrOpenBlob !== 'undefined') {
                return navigator.msSaveOrOpenBlob(file, fileFullName);
            }
            else if (typeof navigator.msSaveBlob !== 'undefined') {
                return navigator.msSaveBlob(file, fileFullName);
            }

            var hyperlink = document.createElement('a');
            hyperlink.href = URL.createObjectURL(file);
            hyperlink.download = fileFullName;

            hyperlink.style = 'display:none;opacity:0;color:transparent;';
            (document.body || document.documentElement).appendChild(hyperlink);

            if (typeof hyperlink.click === 'function') {
                hyperlink.click();
            }
            else {
                hyperlink.target = '_blank';
                hyperlink.dispatchEvent(new MouseEvent('click',
                                                       {view: window,
                                                        bubbles: true,
                                                        cancelable: true}));
            }

            URL.revokeObjectURL(hyperlink.href);
        }
    };

    return app;
});
