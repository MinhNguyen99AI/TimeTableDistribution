import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadFileZoneComponent } from './upload-file-zone.component';

describe('UploadFileZoneComponent', () => {
  let component: UploadFileZoneComponent;
  let fixture: ComponentFixture<UploadFileZoneComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UploadFileZoneComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UploadFileZoneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
