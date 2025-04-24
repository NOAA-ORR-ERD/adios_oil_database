import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import fetch from 'fetch';


const allowedTypes = [
    'text/csv',
    'text/tab-separated-values',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf',
    'application/json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];


export default class TabPaneAttachments extends Component {
  @tracked attachmentList;
  @tracked duplicateAttachment = {};
  @tracked dialogVisible = false;
  @tracked error;

  constructor() {
    super(...arguments);

    this.getAttachmentList();
  }

  validateFile(file) {
    return allowedTypes.includes(file.type);
  }

  @action
  async submitAttachmentForUpload(attachment) {
    if (this.attachmentList.map(i => i.filename).includes(attachment.file.name)) {
        this.duplicateAttachment = attachment;
        this.show_dialog();
    }
    else {
        this.uploadAttachment(attachment);
    }
  }

  @action
  async uploadAttachment(attachment) {
    let webApi = this.args.webApi;
    let oilId = this.args.oil.oil_id;


    try {
      let options = {};

      options.withCredentials = true;
      options.headers = {
        'filename': attachment.file.name,
      };

      const response = await attachment.uploadBinary(
        `${webApi}/attachments/${oilId}/`,
        options
      );

      this.getAttachmentList();
    } catch (response) {
      console.error(`File upload failed: ${response}`);
    }
  }

  @action
  async deleteAttachment(index) {
    let filename = this.attachmentList[index].filename;

    const url = `${this.args.webApi}/attachments/${this.args.oil.oil_id}/${filename}`;
    const options = {
      method: 'DELETE',
    };

    fetch(url, options)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then(data => {
      console.log('Successfully deleted attachment: ', data);
      this.getAttachmentList();
    })
    .catch(error => {
      console.error('Error deleting attachment:', error);
    });
  }

  @action
  async updateAttachment(index) {
    let attachment = this.attachmentList[index];

    const url = `${this.args.webApi}/attachments/${this.args.oil.oil_id}/`;
    const options = {
      method: 'PUT',
      headers: {
          "Content-Type": attachment.contentType,
          'filename': attachment.filename,
          'fields-only': 'true',
          'comments': btoa(attachment.comments),
      },
    };

    fetch(url, options)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then(data => {
      console.log('Successfully updated attachment: ', data);
      this.getAttachmentList();
    })
    .catch(error => {
      console.error('Error updating resource:', error);
    });
  }

  @action
  async getAttachmentList() {
    try {
      const response = await fetch(`${this.args.webApi}/attachments/${this.args.oil.oil_id}/`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      this.attachmentList = await response.json();
    } catch (e) {
      this.error = e;
    }
  }

  @action
  show_dialog(event) {
      this.dialogVisible = true;
  }

  @action
  close_dialog(event) {
      this.dialogVisible = false;
  }

  @action
  submit_dialog(attachment) {
      this.uploadAttachment(attachment);
      this.dialogVisible = false;
  }

}
