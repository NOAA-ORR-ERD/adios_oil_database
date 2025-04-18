import { module, test } from 'qunit';
import { setupRenderingTest } from 'adios-db/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | tab-pane/attachments', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<TabPane::Attachments />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <TabPane::Attachments>
        template block text
      </TabPane::Attachments>
    `);

    assert.dom().hasText('template block text');
  });
});
