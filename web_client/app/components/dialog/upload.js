import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";

export default class UploadDlg extends Component {
    @tracked file;

    get formFilledOut() {
        if (this.file) {
            return true;
        }

        return false;
    }

    @action uploadedFile(data) {
        let oilData = JSON.parse(data);

        oilData['productType'] = oilData['product_type']
        oilData['referenceDate'] = oilData['reference_date']

        delete oilData['id'];

        this.args.submit(oilData);
    }

    @action
    updateFile(event) {
        if (event.target.files.length) {
            this.file = event.target.files[0];
        }
        else {
            this.file = null;
        }

    }

    @action
    submitForm() {
        const reader = new FileReader();
        const file = this.file;

        // Note: reading file is async
        reader.onload = () => {
            this.uploadedFile(reader.result);
        };

        if (file) {
            reader.readAsText(file);
        }

    }

}
