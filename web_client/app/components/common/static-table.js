import Component from '@glimmer/component';

export default class StaticTable extends Component {

    constructor() {
        super(...arguments);
        {{debugger}}

        this.propertyTypesObj = this.readPropertyTypes(this.args.store, this.args.propertyName + ".json");
        delete this.propertyTypesObj.id;
        this.typeKeys = Object.keys(this.propertyTypesObj);
    }

    readPropertyTypes(store, propertyFileName) {

        // hard coding - TODO - read it from 'public/config' folder
        //    store.findRecord('config', propertyFileName);

        return {
            id: "sara-total-fractions.json",
            saturates: {
              label: "Saturates",
              inputType: "range"
            },
            aromatics: {
              label: "Aromatics",
              inputType: "range"
            },
            resins: {
              label: "Resins",
              inputType: "range"
            },
            asphaltenes: {
              label: "Asphaltenes",
              inputType: "range"
            }
                                 
        };


        // return async function () {
        //     let data = await store.findRecord('config', 'sara_total_fractions.json');
        //     let types = JSON.parse(data);
        //     return types;
        // }();
    }
}
