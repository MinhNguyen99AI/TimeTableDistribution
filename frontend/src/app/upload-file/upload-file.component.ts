import { Component, Input, OnInit, Output } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { PopupComponent } from '../popup/popup.component';
import { BaseModel, FileWithType, UploadFileRequest } from '../shared/model/file.model';
import { UploadFileService } from '../shared/service/upload-file.service';

@Component({
  selector: 'app-upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.scss'],
  providers: [
  ]
})
export class UploadFileComponent implements OnInit {
  files: Array<FileWithType> = new Array;

  constructor(
    private dialog: MatDialog,
    private uploadFileService: UploadFileService,
    private router: Router
  ) { }
  
  ngOnInit(): void {
  }

  uploadFile(files: Array<FileWithType>) {
    console.log(files);
    this.files = files;
  }

  onMergeClick() {
    console.log("Merge button click!");
    if (this.files.length !== 3) {
      this.dialog.open(PopupComponent,{ data: {
        message:  "You not upload enough file"
      }});
    }
    let request: UploadFileRequest = {};
    for (let file of this.files) {
      let baseModel: BaseModel = { data: file.data, name: file.name };
      if (file.type === "School") {
        request.schoolData = baseModel;
      } else if (file.type === "Foreign") {
        request.teacherForeignData = baseModel;
      } else {
        request.teacherDomesticData = baseModel;
      }
    }

    this.uploadFileService.uploadFile(request)
    .subscribe(res => {
      console.log('fileId: ', res);
      this.router.navigate(['/loading', { fileId: res.id }])
    });
  }
}
