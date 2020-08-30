import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';


export default class SelectUnitButton extends Component {
  @tracked baseProperty;
  @tracked element;
  @tracked selectingUnit = false;

  constructor() {
      super(...arguments);

      this.baseProperty = this.args.baseProperty;
  }

  @action
  setComponentElement(element) {
      this.element = element;
  }

  @action
  launchSelectDialog() {
    this.selectingUnit = true;
  }

  @action
  closeSelectDialog() {
    this.selectingUnit = false;
  }

}
