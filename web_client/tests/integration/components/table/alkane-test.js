import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | table/alkane', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`{{table/alkane}}`);

    assert.dom(this.element).hasText('');

    // Template block usage:
    await render(hbs`
      <Table::Alkane>
        template block text
      </Table::Alkane>
    `);

    assert.dom(this.element).hasText('template block text');
  });
});
