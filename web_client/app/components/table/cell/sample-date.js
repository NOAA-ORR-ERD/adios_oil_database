import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

export default class SampleDate extends Component {
    @tracked sampleYear;

    constructor() {
        super(...arguments);
        
        let sampleDate = this.args.row.content.metadata.sample_date;
        this.sampleYear = (sampleDate.match(/^\d{4}/)||[])[0];
    }
}
