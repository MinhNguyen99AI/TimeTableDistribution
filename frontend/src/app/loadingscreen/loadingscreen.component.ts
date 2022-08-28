import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { delay } from 'lodash';
import { map, Observable, Subscription, timer, Timestamp } from 'rxjs';
import { subscriptionLogsToBeFn } from 'rxjs/internal/testing/TestScheduler';
import { PopupComponent } from '../popup/popup.component';
import { CheckStatusRequest } from '../shared/model/file.model';
import { UploadFileService } from '../shared/service/upload-file.service';

@Component({
  selector: 'app-loadingscreen',
  templateUrl: './loadingscreen.component.html',
  styleUrls: ['./loadingscreen.component.scss']
})
export class LoadingscreenComponent implements OnInit, OnDestroy {
  result$: Subscription | undefined;
  progress$: Subscription | undefined;
  public percentage: number;

  constructor(
    private dialog: MatDialog,
    private route: ActivatedRoute,
    private router: Router,
    private uploadFileService: UploadFileService
  ) {
    this.percentage = 0;
  }

  ngOnInit(): void {
    let startTime: Date = new Date();
    const fileId = this.route.snapshot.paramMap.get('fileId');
    let checkStatusRequest : CheckStatusRequest = {};
    checkStatusRequest.fileId = fileId as string;
    this.result$ = timer(0, 60000).pipe( 
      map(() => { 
        this.uploadFileService.checkStatus(checkStatusRequest)
        .subscribe( res => {
          let currentTime: Date = new Date();
          if (currentTime.getTime() - startTime.getTime() > 60 * 60 * 1000) {
            this.dialog.open(PopupComponent,{ data: {
              message:  "Không có kết quả trả về. Vui lòng liên hệ minhchanh991@gmail.com để tìm cách khắc phục."
            }});
            this.router.navigate([''])
          }
          if (res.status == "FINISHED") {
            setTimeout(() => 2000);
            this.result$?.unsubscribe();
            this.router.navigate(['/download-file', { fileId: fileId }])
          }
        }); 
      }) 
    ).subscribe(); 
    this.progress$ = timer(0, 14000).pipe(
      map(() => this.loading("null"))
    ).subscribe();
  }
  
  ngOnDestroy(): void {
    this.result$?.unsubscribe();
  }

  loading(status: string) {
    if (this.percentage < 90) {
      this.percentage += 1;
      let endWidth = this.percentage;
      // switch (status){
      //   case "PENDING":
      //     endWidth = 10;
      //     break;
      //   case "SCHOOL_COORDINATE_DONE":
      //     endWidth = 26;
      //     break;
      //   case "FOREIGN_COORDINATE_DONE":
      //     endWidth = 42;
      //     break;
      //   case "MATCHED_FOREIGN":
      //     endWidth = 58;
      //     break;
      //   case "DOMESTIC_COORDINATE_DONE":
      //     endWidth = 74;
      //     break;
      //   case "MATCHED_DOMESTIC":
      //     endWidth = 90;
      //     break;
      //   case "FINISHED":
      //     endWidth = 100;
      //     break;
      //   default:
      //     endWidth = 0;
      // }
      let current = document.querySelector(".bar") as HTMLElement;
      current.style.width = `${endWidth}%`;
      (current.firstElementChild! as HTMLElement).innerText = `${endWidth}%`;
    }
  }
}
