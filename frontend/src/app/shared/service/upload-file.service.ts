import { Injectable } from '@angular/core';
import { CheckStatusRequest, CheckStatusResponse, GetResultRequest, GetResultResponse, UploadFileRequest, UploadFileResponse } from '../model/file.model';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UploadFileService {

  constructor(private http: HttpClient) { }
  private uploadFileApi = 'http://localhost:5000/match';
  private checkStatusApi = 'http://localhost:5000/status';
  private getResultApi = 'http://localhost:5000/result';

  uploadFile(uploadFilerequest: UploadFileRequest) {
    return this.http.post<UploadFileResponse>(this.uploadFileApi, uploadFilerequest);
  }

  checkStatus(checkStatusRequest: CheckStatusRequest) {
    const fileId = checkStatusRequest.fileId;
    return this.http.get<CheckStatusResponse>(this.checkStatusApi + "?id=" + fileId);
  }

  getResult(getResultRequest: GetResultRequest) {
    const fileId = getResultRequest.fileId;
    return this.http.get(this.getResultApi + "?id=" + fileId, {
      responseType: 'arraybuffer'
    });
  }
}
