import { module, test } from 'qunit';
import { setupApplicationTest } from 'ember-qunit';
import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import {
  click,
  currentURL,
  visit,
  fillIn,
  triggerKeyEvent
} from '@ember/test-helpers';

module('Acceptance | list oils', function(hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  test('should show oils as the home page', async function (assert) {
    await visit('/');
    assert.equal(currentURL(), '/oils', 'should redirect automatically');
  });

  test('should link to information about NOAA.', async function (assert) {
    await visit('/');
    await click(".menu-about");

    assert.equal(currentURL(), '/about', 'should navigate to about');
  });

  test('should link to contact information.', async function (assert) {
    await visit('/');
    await click(".menu-contact");

    assert.equal(currentURL(), '/contact', 'should navigate to contact');
  });

  test('should list available oils.', async function (assert) {
    await visit('/');
    assert.equal(this.element.querySelectorAll('.listing').length, 4,
                 'should display 4 listings');
  });

  test('should filter the list of oils by name.', async function (assert) {
    await visit('/');
    await fillIn('.list-filter input', 'castor oil');
    await triggerKeyEvent('.list-filter input', 'keyup', 69);

    assert.equal(this.element.querySelectorAll('.results .listing').length, 1,
                 'should display 1 listing');
    assert.ok(this.element.querySelector('.listing h3').textContent.includes('CASTOR OIL'),
              'should contain 1 listing with location Seattle');
  });

  test('should show details for a selected oil', async function (assert) {
    await visit('/oils');
    await click(".AD01988");
    
    assert.equal(currentURL(), '/oils/AD01988',
                 'should navigate to show route');
    assert.ok(this.element.querySelector('.show-listing h2').textContent
              .includes('ALASKA NORTH SLOPE (NORTHERN PIPELINE, 1999)'),
              'should list oil name');
    assert.ok(this.element.querySelector('.detail-section .id').textContent.trim()
              .includes('ID: AD01988'),
              'should list oil id');
  });

});
