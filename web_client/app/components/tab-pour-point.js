import Component from '@glimmer/component';

export default class TabPourPoint extends Component {
    
    constructor() {
        super(...arguments);

    }
    
    get editable() {
        return this.args.editable;
    }

}