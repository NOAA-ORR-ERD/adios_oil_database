import Component from '@glimmer/component';

export default class Status extends Component {
    get hasErrors() {
        let value = this.args.value;

        if (value && value.length > 0) {
            return value.map(i => {
                return i.substring(0, 1) == 'E'
            }).reduce((sum, i) => sum || i, false);
        }
        else {
            return false;
        }
    }

    get hasWarnings() {
        let value = this.args.value;

        if (value && value.length > 0) {
            return value.map(i => {
                return i.substring(0, 1) == 'W'
            }).reduce((sum, i) => sum || i, false);
        }
        else {
            return false;
        }
    }

}
