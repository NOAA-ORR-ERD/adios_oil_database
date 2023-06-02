'use strict';

module.exports = function(environment) {
  let ENV = {
    modulePrefix: 'adios-db',
    environment,
    rootURL: '/',
    locationType: 'auto',

    moment: {
      // Options:
      // 'all' - all years, all timezones
      // '2010-2020' - 2010-2020, all timezones
      // 'none' - no data, just timezone API
      includeTimezone: 'all',
      allowEmpty: true
    },

    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. EMBER_NATIVE_DECORATOR_SUPPORT: true
      },
      EXTEND_PROTOTYPES: {
        // Prevent Ember Data from overriding Date.parse.
        Date: false
      }
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
    }
  };

  ENV['ember-cli-mirage'] = {
    enabled: false
  };

  ENV['ember-toggle'] = {
    includedThemes: [],
    excludedThemes: [],
    excludeBaseStyles: false, // defaults to false
    defaultShowLabels: true,  // defaults to false
    defaultTheme: 'ios',    // defaults to 'default'
    defaultSize: 'small',     // defaults to 'medium'
    defaultOffLabel: 'False', // defaults to 'Off'
    defaultOnLabel: 'True'    // defaults to 'On'
  };

  ENV['contentSecurityPolicy'] = {
      'default-src': "'none'",
      'script-src': "'self' www.google-analytics.com",
      'font-src': "'self'",
      'connect-src': "'self' http://localhost:9898 www.google-analytics.com",
      'img-src': "'self'",
      'style-src': "'self'",
      'media-src': "'self'"
  };

  if (environment === 'development') {
    ENV['metricsAdapters'] = [
        {
          name: 'GoogleAnalyticsFour',
          environments: ['development'],
          config: {
            id: 'G-FFPE4N76NB',
            options: {
              anonymize_ip: true,
              debug_mode: true,
            },
          },
        },
    ];
  }
  else if (environment === 'production') {
    ENV['metricsAdapters'] = [
        {
          name: 'GoogleAnalyticsFour',
          environments: ['production'],
          config: {
            id: 'G-4M4CJVKWYN',
            options: {
              anonymize_ip: true,
              debug_mode: false,
            },
          },
        },
    ];
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
    ENV.APP.autoboot = false;
  }

  return ENV;
};
