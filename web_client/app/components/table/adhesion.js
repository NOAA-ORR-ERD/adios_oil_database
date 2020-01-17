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
    updateAdhesion(e) {

        // if (isNaN(e.target.value)) {
        //     if (this.adhesion) {
        //         this.adhesion = undefined;
        //     }
        // } else {
        //     if (this.adhesion) {
        //         this.adhesion.adhesion.value = Number(e.target.value);
        //     } else {
        //         let adhesion = {};
        //         adhesion.value = Number(e.target.value);
        //         adhesion.unit = "N/m^2";
        //         //this.adhesion.pushObject(adhesion);
        //     }
        // }
        // TODO - No Data case
        //this.args.submit(this.args.oil);
    }
}