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
        let oilData;

        if (data) {
            try {
                oilData = JSON.parse(data);
            }
            catch(e) {
                alert("File Loading Error: " +
                      "This does not look like a valid ADIOS database " +
                      "JSON file. Please check the filename and try again.");
                return;
            }
        }
        else {
            alert('File is empty!');
            return;
        }

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
