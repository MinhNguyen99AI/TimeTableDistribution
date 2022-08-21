import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DownloadFileComponent } from './download-file/download-file.component';
import { LoadingscreenComponent } from './loadingscreen/loadingscreen.component';
import { UploadFileComponent } from './upload-file/upload-file.component';

const routes: Routes = [
  { path: '', component: UploadFileComponent },
  { path: 'download-file', component: DownloadFileComponent },
  { path: 'loading', component: LoadingscreenComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
