import { Component, EventEmitter, Input, OnInit, Output, Renderer2 } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import * as _ from 'lodash';
import { Observable, ReplaySubject } from 'rxjs';
import { PopupComponent } from 'src/app/popup/popup.component';
import { FileWithType } from 'src/app/shared/model/file.model';

@Component({
  selector: 'app-upload-file-zone',
  templateUrl: './upload-file-zone.component.html',
  styleUrls: ['./upload-file-zone.component.scss'],
})
export class UploadFileZoneComponent implements OnInit {
  @Output() fileUploaded = new EventEmitter<any>();
  fileSchoolName: string = '';
  fileSchoolSize: any;
  fileForeignName: string = '';
  fileForeignSize: any;
  fileVNName: string = '';
  fileVNSize: any;
  notUploadSchool: boolean = true;
  notUploadForeign: boolean = true;
  notUploadVN: boolean = true;
  files: Array<any> = new Array;

  constructor(
    private dialog: MatDialog,
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  handleUploadFile(event: any, type: string) {
    let af = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    if (event.target.files.length > 0) {
      const file = event.target.files[0];

      if (!_.includes(af, file.type)) {
        this.dialog.open(PopupComponent,{ data: {
          message:  file.name
        }, panelClass: 'custom-dialog-container'});
      } else {

        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            let encoded = reader.result!.toString().replace(/^data:(.*,)?/, '');
            if ((encoded.length % 4) > 0) {
              encoded += '='.repeat(4 - (encoded.length % 4));
            }
            let fileWithType: FileWithType = {name: file.name, data: encoded, type: type};
            if (type === "School"){
              this.notUploadSchool = false;
              this.fileSchoolName = file.name;
              this.fileSchoolSize = file.size;
            } else if (type === "Foreign") {
              this.notUploadForeign = false;
              this.fileForeignName = file.name;
              this.fileForeignSize = file.size;
            } else {
              this.notUploadVN = false;
              this.fileVNName = file.name;
              this.fileVNSize = file.size;
            }
            
            this.files.push(fileWithType);
            this.fileUploaded.emit(this.files);
        };
      }
    }
  }

  onFileSchoolSelect(event: any) {
    this.handleUploadFile(event, "School");
  }
  onFileForeignSelect(event: any) {
    this.handleUploadFile(event, "Foreign");
  }
  onFileVNSelect(event: any) {
    this.handleUploadFile(event, "VN");
  }

  garbargeBtnSchoolClick() {
    this.notUploadSchool = true;
    this.files.forEach((file,index)=>{
      if(file.type === "School") this.files.splice(index,1);
   });
   console.log(this.files);
  }

  garbargeBtnForeignClick() {
    this.notUploadForeign = true;
    this.files.forEach((file,index)=>{
      if(file.type === "Foreign") this.files.splice(index,1);
   });
   console.log(this.files);
  }

  garbargeBtnVNClick() {
    this.notUploadVN = true;
    this.files.forEach((file,index)=>{
      if(file.type === "VN") this.files.splice(index,1);
   });
   console.log(this.files);
  }
}
