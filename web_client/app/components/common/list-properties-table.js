import Component from '@glimmer/component';

export default class ListPropertiesTable extends Component {
    // Common component to take a passed-in property name and produce a table
    // from the data contained within.
    // - The property name will be assumed to belong to an oil/sample object
    //   and contain a JS object with a number of named attributes to be read
    //   to form the values in the table.
    // - A template name will be passed in.  The associated template file
    //   will be a JSON object that determines which attributes will be
    //   included in the table.
    //
    // Required parameters:
    // - @oil: The base oil/sample object
    // - @store: the model datastore
    // - @submit: The oil submit function.
    // - @editable (boolean): Make the table editable.
    // - @tableTitle (string): The title of the table.
    // - @propertyName (string): the oil property to read.
    //
    // Optional parameters:
    // - @templateName (string): The name of the template used to format the
    //                           table.
    // - @boldTitle (boolean): This sets the title of the table to bold.
    // - @headerPosition (string): This determines whether to put the header of
    //                             the table on top or to the side.  Values are
    //                             "top" (default), or "side".
    constructor() {
        super(...arguments);

        // all we are doing is passing these to the real components,
        // but we want some arguments to be optional.  And for some reason,
        // ember gives an error if an argument is used but not passed in.
        // So it is necessary to establish top-level class attributes in case
        // the arguments are not passed.  
        this.templateName = this.args.templateName;
        this.boldTitle = this.args.boldTitle;
        this.headerPosition = this.args.headerPosition;
    }
}
