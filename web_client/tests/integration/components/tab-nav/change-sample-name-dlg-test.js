import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | tab-nav/change-sample-name-dlg', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<TabNav::ChangeSampleNameDlg />`);

    assert.equal(this.element.textContent.trim(), '');

    // Template block usage:
    await render(hbs`
      <TabNav::ChangeSampleNameDlg>
        template block text
      </TabNav::ChangeSampleNameDlg>
    `);

    assert.equal(this.element.textContent.trim(), 'template block text');
  });
});
