import Component from '@glimmer/component';

export default class ListPropertiesTable extends Component {
    constructor() {
        super(...arguments);

        // all we are doing is passing these to the real components,
        // but we want some arguments to be optional.  And for some reason,
        // ember gives an error if an argument is used but not passed in.
        // So it is necessary to establish class values in case the arguments
        // are not passed.  
        this.templateName = this.args.templateName;
        this.boldTitle = this.args.boldTitle;
        this.headerPosition = this.args.headerPosition;
    }
}
