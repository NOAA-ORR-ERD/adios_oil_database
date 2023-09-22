import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | table/conradson', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`{{table/conradson}}`);

    assert.dom(this.element).hasText('');

    // Template block usage:
    await render(hbs`
      <Table::Conradson>
        template block text
      </Table::Conradson>
    `);

    assert.dom(this.element).hasText('template block text');
  });
});
