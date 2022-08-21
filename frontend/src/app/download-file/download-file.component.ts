import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { GetResultRequest } from '../shared/model/file.model';
import { UploadFileService } from '../shared/service/upload-file.service';

@Component({
  selector: 'app-download-file',
  templateUrl: './download-file.component.html',
  styleUrls: ['./download-file.component.scss']
})
export class DownloadFileComponent implements OnInit {
  fileId: string | undefined;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private uploadFileService: UploadFileService
  ) { }

  ngOnInit(): void {
    this.fileId = this.route.snapshot.paramMap.get('fileId') as string;
  }

  onDownloadClick(){
    let request: GetResultRequest = {};
    request.fileId = this.fileId;
    this.uploadFileService.getResult(request)
    .subscribe(res => {
      const blob = new Blob([res], {
        type: 'application/zip'
      });
      const url = window.URL.createObjectURL(blob);
      window.open(url);
    });    
  }
}
