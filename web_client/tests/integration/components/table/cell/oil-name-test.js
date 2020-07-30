import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | oil-name-cell', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<OilNameCell />`);

    assert.dom(this.element).hasText('');

    // Template block usage:
    await render(hbs`
      <OilNameCell>
        template block text
      </OilNameCell>
    `);

    assert.dom(this.element).hasText('template block text');
  });
});
