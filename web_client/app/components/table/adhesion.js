import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class Adhesion extends Component {

    @tracked adhesion;

    constructor() {
        super(...arguments);
        this.adhesion = this.args.oil.adhesion;
        {{debugger}}
    }

    @action
    updateAdhesion(e) {
        {{debugger}}
        // let adhesion = {};
        // adhesion["value"] = Number(e.target.value);
        // adhesion["unit"] = "N/m^2"
        if(this.adhesion) {
            this.adhesion.adhesion.value = Number(e.target.value);
        }
        // TODO - No Data case
        //this.args.submit(this.args.oil);
    }

}