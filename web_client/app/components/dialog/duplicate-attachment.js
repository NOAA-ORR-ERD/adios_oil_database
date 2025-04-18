import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from "@ember/object";
import { ref } from 'ember-ref-bucket';

import { UploadFile, FileSource } from 'ember-file-upload';


export default class DialogDuplicateAttachment extends Component {
    @tracked attachmentName;
    @ref("okButton") okButton;

    constructor() {
        super(...arguments);

        this.attachmentName = this.args.attachment.name;
    }

    get formFilledOut() {
        if (this.attachmentName) {
            return true;
        }

        return false;
    }

    @action
    updateAttachmentName(event) {
        this.attachmentName = event.currentTarget.value;

        if (['change', 'focusout'].includes(event.type) && this.formFilledOut) {
            this.okButton.focus();
        }
    }

    @action
    closeForm() {
        this.args.close();
    }

    @action
    submitForm() {
        let attachment = new UploadFile(
            new File(
                [this.args.attachment.file],
                this.attachmentName,
                {type: this.args.attachment.file.type}
            ),
            FileSource.DragAndDrop
        );

        this.args.submit(
            attachment
        );
    }
}
