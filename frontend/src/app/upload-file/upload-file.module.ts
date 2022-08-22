import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadFileZoneComponent } from './upload-file-zone/upload-file-zone.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    UploadFileZoneComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  exports: [
    UploadFileZoneComponent
  ]
})
export class UploadFileModule { }
