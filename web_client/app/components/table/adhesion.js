import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Adhesion extends Component {

    @tracked adhesion;

    constructor() {
        super(...arguments);

        this.adhesion = this.args.oil.adhesion;
    }

    @action
    updateAdhesion() {
        this.args.oil.adhesion = this.adhesion;
    }

}