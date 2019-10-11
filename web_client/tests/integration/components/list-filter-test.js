import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, settled, triggerKeyEvent, fillIn } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

const ITEMS = [
  {name: 'ALASKA NORTH SLOPE (NORTHERN PIPELINE, 1999)'},
  {name: 'CASTOR OIL'},
  {name: 'Cold Lake Winter Blend 2015'},
  {name: 'Alaska North Slope [2015]'}
];
const FILTERED_ITEMS = [{name: 'CASTOR OIL'}];

module('Integration | Component | list-filter', function(hooks) {
  setupRenderingTest(hooks);

  test('should initially load all listings', async function (assert) {
    // we want our actions to return promises, since they are potentially
    // fetching data asynchronously.
    this.set('filterByName', () => Promise.resolve({ results: ITEMS }));

    // with an integration test, you can set up and use your component in the
    // same way your application will use it.
    await render(hbs`
      <ListFilter @filter={{action filterByName}} as |results|>
        <ul>
        {{#each results as |item|}}
          <li class="name">
            {{item.name}}
          </li>
        {{/each}}
        </ul>
      </ListFilter>
    `);

    await settled();

    assert.equal(this.element.querySelectorAll('.name').length, 4);
    assert.dom(this.element.querySelector('.name'))
      .hasText('ALASKA NORTH SLOPE (NORTHERN PIPELINE, 1999)');

  });

  test('should update with matching listings', async function (assert) {
    this.set('filterByName', (val) => {
      if (val === '') {
        return Promise.resolve({
          query: val,
          results: ITEMS });
      }
      else {
        return Promise.resolve({
          query: val,
          results: FILTERED_ITEMS });
      }
    });

    await render(hbs`
      <ListFilter @filter={{action filterByName}} as |results|>
        <ul>
        {{#each results as |item|}}
          <li class="name">
            {{item.name}}
          </li>
        {{/each}}
        </ul>
      </ListFilter>
    `);

    // fill in the input field with 's'
    await fillIn(this.element.querySelector('.list-filter input'),'s');
    // keyup event to invoke an action that will cause the list to be filtered
    await triggerKeyEvent(this.element.querySelector('.list-filter input'), "keyup", 83);
    await settled();

    assert.equal(this.element.querySelectorAll('.name').length, 1, 'One result returned');
    assert.dom(this.element.querySelector('.name')).hasText('CASTOR OIL');
  });

});
