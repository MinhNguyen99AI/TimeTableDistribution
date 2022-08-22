export interface BaseModel {
    name?: string;
    data?: any;
}

export interface FileWithType extends BaseModel{
    type?: any;
}

export interface UploadFileRequest {
    schoolData?: BaseModel;
    teacherDomesticData?: BaseModel;
    teacherForeignData?: BaseModel;
}

export interface UploadFileResponse {
    id?: string;
}

export interface CheckStatusRequest {
    fileId?: string;
}

export interface CheckStatusResponse {
    status: string;
}

export interface GetResultRequest {
    fileId?: string;
}

export interface GetResultResponse {
    zipFile: any;
}