define([
    'jquery',
    'underscore',
    'backbone',
    'model/oil/library',
    'text!templates/oil/specific.html'
], function($, _, Backbone, OilLib, SpecificOilTemplate){
    'use strict';
	var specificOil = Backbone.View.extend({
		id: 'specificOilContainer',

        events: {
            'shown.bs.tab': 'tabRender'
        },

		initialize: function(options){
            if (!_.isUndefined(options.containerClass)) {
                this.containerClass = options.containerClass;
                this.viewName = 'oilInfo';
            } else {
                this.viewName = 'oilLib';
            }

            if (!_.isUndefined(options.infoMode)) {
                options.model.fetch({
                    success: _.bind(function(model){
                        this.model = model;
                        this.render(options);
                    }, this)
                });
            } else {
                this.render(options);
                this.tabRender();
            }
		},

		render: function(options){
			var data = this.dataParse(this.model.attributes);
            var viewName = this.viewName;
			var compiled = _.template(SpecificOilTemplate, {data: data, viewName: viewName});
            if (!_.isUndefined(this.containerClass)) {
                var containerClass = this.containerClass;
                $(containerClass + ' .modal-body').append(this.$el.html(compiled));
            } else {
                $('.oil-form .modal-body').append(this.$el.html(compiled));
            }
		},

        tabRender: function(){
            this.$('.info:visible').tooltip({
                container: '.modal'
            });
        },
        
        kToC: function(k){
        	// Kelvin to Celcius
        	return (k - 273.15).toFixed(1);
        },

        cToF: function(c){
        	// Celcius to Farenheit
            return ((c * 9.0 / 5.0) + 32.0).toFixed(1);
        },

        kToF: function(k){
        	// Kelvin to Farenheit
        	return this.cToF(this.kToC(k));
        },

        doNotEvaluate: ["estimated"],

        groupAnalysis: ['aromatics_fraction',
			            'polars_fraction',
			            'resins_fraction',
			            'saturates_fraction',
			            'paraffins_fraction',
			            'sulphur_fraction',
			            'benzene_fraction',
			            'wax_content_fraction',
			            'asphaltenes_fraction'],

        tempAttrs: ['ref_temp_k',
		            'liquid_temp_k',
		            'vapor_temp_k'],

        tempRangeAttrs: ['pour_point_min_k',
			             'pour_point_max_k',
			             'flash_point_min_k',
			             'flash_point_max_k'],

		dataParse: function(oilParam, estimatedObj){
            var oil = $.extend(true, {}, oilParam);

            console.log("entering dataParse()...");

            this.traverseOil("oil", oil, this.processOilNode);
            console.log("completed traversing oil structure...");

            // Set the initial estimated object.
            // We will then pass it on to recursed calls
            if (!estimatedObj && oil.estimated) {
            	estimatedObj = oil.estimated;
            	this.populateTemperatureEstimationFlags(estimatedObj);
            }

        	for (var attr in oil) {
        		// determine if the attribute is estimated.
        		if (estimatedObj[attr]) {
        			oil[attr] = '<code>' + oil[attr] + '</code>';
        		}
        	}

            return oil;
		},

		traverseOil: function(parentAttr, o, func) {
		    for (var i in o) {
		        func.apply(this, [parentAttr, o, i]);  

		        if ($.inArray(i, this.doNotEvaluate) >= 0) {
		        	continue;
		        }

		        if (o[i] !== null && typeof(o[i]) === "object") {
		            //going on step down in the object tree!!
		        	this.traverseOil(i, o[i], func);
		        }
		    }
		},

		processOilNode: function(parentAttr, parentObj, key) {
		    // console.log(parentAttr + "[" + key + "] : " + parentObj[key]);

		    this.parseTemperatureRangeData(parentObj, key);
			this.parseTemperatureData(parentObj, key);

		    this.parseGroupAnalysis(parentObj, key);

		    if (parentObj[key] === null) {
            	// When value of oil attribute is null
                parentObj[key] = "--";
            }
            else if (key === 'bullwinkle_fraction')
            {
                parentObj[key] = parentObj[key].toFixed(2);
            }
            else if (key === 'oil_seawater_interfacial_tension_n_m' ||
            		 key === 'oil_water_interfacial_tension_n_m')
            {
               	// convert to cSt
            	parentObj[key] = (parentObj[key] * 1000).toFixed(1);
            }
            else if (key === 'api') {
            	parentObj[key] = parentObj[key].toFixed(1);
            }
            else if (key === 'weathering') {
            	parentObj[key] = parentObj[key].toFixed(1);
            }
            else if (key === 'kg_m_3') {
            	parentObj[key] = parentObj[key].toFixed(2);
            }
            else if (key === 'categories') {
                for (var i = 0; i < parentObj[key].length; i++) {
                    var parentCategory = parentObj[key][i].parent.name;
                    var childCategory = parentObj[key][i].name;
                    parentObj[key][i] = parentCategory + '-' + childCategory;
                }
            }
		},

		parseTemperatureRangeData: function(oil, attr) {
            if ($.inArray(attr, this.tempRangeAttrs) >= 0) {
            	// we are one of the registered min/max temperature attrs
                if (oil[attr] === null) {
                	// we don't have a value
                	// basically these are min/max pair values, and if
                	// one of them is missing, we just copy from the other
                	// attribute in the pair
                	var other_suffix = "";
                	if (attr.indexOf("_max_k") === attr.length - 6) {
                		other_suffix = "_min_k";
                    }
                	else if (attr.indexOf("_min_k") === attr.length - 6) {
                		other_suffix = "_max_k";
                    }

                    var other_attr = attr.substring(0, attr.length - 6) +
                    				 other_suffix;

                    if (oil[other_attr] === null) {
                    	// neither attribute in the pair have a value
                    	oil[attr] = "--";
                    }
                    else {
                    	oil[attr] = oil[other_attr];
                    }
                }

                // we should have a valid value at this point
                var attr_c = attr.substring(0, attr.length - 2) + '_c';
                var attr_f = attr.substring(0, attr.length - 2) + '_f';
                

                if (oil[attr] === "--") {
                	oil[attr_c] = oil[attr_f] = "--";
                }
                else {
                	oil[attr_c] = this.kToC(oil[attr]);
                	oil[attr_f] = this.kToF(oil[attr]);
                }
            }
        },

		parseTemperatureData: function(obj, key) {
            if ($.inArray(key, this.tempAttrs) >= 0) {
            	// we are one of the registered temperature attrs
                if (obj[key] === null) {
                	obj[key] = "--";
                }

                // we should have a valid value at this point
                var key_c = key.substring(0, key.length - 2) + '_c';
                var key_f = key.substring(0, key.length - 2) + '_f';

                if (obj[key] === "--") {
                	obj[key_c] = obj[key_f] = "--";
                }
                else {
                	obj[key_c] = this.kToC(obj[key]);
                	obj[key_f] = this.kToF(obj[key]);
                }
            }
        },

        populateTemperatureEstimationFlags: function(estimated) {
        	for (var idx in this.tempRangeAttrs) {
        		var attr = this.tempRangeAttrs[idx];
                if (estimated[attr] !== null) {
                	var attr_c = attr.substring(0, attr.length - 2) + "_c";
                	var attr_f = attr.substring(0, attr.length - 2) + "_f";

                	estimated[attr_c] = estimated[attr];
                	estimated[attr_f] = estimated[attr];
                }
        	}
        },

        parseGroupAnalysis: function(oil, attr){
            // Checks if oil attribute is one of the group analysis terms
        	// and if so converts to percent
        	if ($.inArray(attr, this.groupAnalysis) >= 0 &&
        			!_.isNull(oil[attr])) {
        		oil[attr] = Math.round((oil[attr] * 100).toFixed(2));

        		if (isNaN(oil[attr])) {
                    oil[attr] = '--';
        		}
            }
        },
	});

	return specificOil;
});
