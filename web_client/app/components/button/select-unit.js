import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';


export default class SelectUnitButton extends Component {
    @tracked baseProperty;
    @tracked element;
    @tracked dialogVisible = false;

    constructor() {
        super(...arguments);

        this.baseProperty = this.args.baseProperty;
    }

    @action
    show_dialog(event) {
        this.dialogVisible = true;
    }

    @action
    close_dialog(event) {
        this.dialogVisible = false;
    }

    @action
    setComponentElement(element) {
        this.element = element;
    }

    @action
    submit(event) {
        this.args.change(event);
    }

}
