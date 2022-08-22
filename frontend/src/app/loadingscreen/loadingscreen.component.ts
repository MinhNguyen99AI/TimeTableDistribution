import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { map, Observable, Subscription, timer } from 'rxjs';
import { CheckStatusRequest } from '../shared/model/file.model';
import { UploadFileService } from '../shared/service/upload-file.service';

@Component({
  selector: 'app-loadingscreen',
  templateUrl: './loadingscreen.component.html',
  styleUrls: ['./loadingscreen.component.scss']
})
export class LoadingscreenComponent implements OnInit {
  result$: Subscription | undefined;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private uploadFileService: UploadFileService
  ) { }

  ngOnInit(): void {
    const fileId = this.route.snapshot.paramMap.get('fileId');
    let checkStatusRequest : CheckStatusRequest = {};
    checkStatusRequest.fileId = fileId as string;
    this.result$ = timer(0, 60000).pipe( 
      map(() => { 
        this.uploadFileService.checkStatus(checkStatusRequest)
        .subscribe( res => {
          if (res.status == "FINISHED") {
            this.result$?.unsubscribe();
            this.router.navigate(['/download-file', { fileId: fileId }])
          }
        }); 
      }) 
    ).subscribe(); 
  }

  ngOnDestroy(): void {
    this.result$?.unsubscribe();
  }
}
