import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | oil-listing', function(hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(function () {
    this.oil = {
      "name": "Fake Oil",
      "id": "EC999999",
      "productType": "crude",
      "location": "Anywhere, Canada",
      "status": ['this is a fake oil'],
      "categoriesStr": "Medium",
      "categories": [
          "Crude-Medium"
      ],
      "pourPoint": [273.15, 273.15],
      "apis": [
          {
              "gravity": 31.32,
              "weathering": 0,
              "_cls": "oil_database.models.oil.api.ApiGravity"
          }
      ],
      "viscosity": 0.001
    };
  });

  test('should display oil details', async function(assert) {
    await render(hbs`<OilListing @oil={{this.oil}} />`);

    assert.equal(this.element.querySelector('.listing h3').textContent.trim(),
                 'Fake Oil',
                 'Title: Fake Oil');
    assert.equal(this.element.querySelector('.listing .id').textContent.trim(),
                 'ID: EC999999',
                 'ID: EC999999');
    assert.equal(this.element.querySelectorAll('.listing .pour-point span').length,
                 3,
                 'Should be 3 span items for pour point');
    assert.equal(this.element.querySelectorAll('.listing .api span').length,
                 2,
                 'Should be 2 span items for API');
  });

});
