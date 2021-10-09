import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { valueUnitUnit } from 'adios-db/helpers/value-unit-unit';
import { convertUnit } from 'adios-db/helpers/convert-unit';
import { valueUnit } from 'adios-db/helpers/value-unit';
import $ from 'jquery';

const ESC_KEY = 27;


export default class MeasurementGroupsDialog extends Component {

    @action
    closeModal() {
        this.args.closeModal();
    }

    @action
    onSave(){
        this.closeModal();
    }
}
