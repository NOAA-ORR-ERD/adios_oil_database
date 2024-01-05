import Component from '@glimmer/component';
import { ref } from 'ember-ref-bucket';


export default class SurveyDialog extends Component {
    @ref("okButton") okButton; 
}
