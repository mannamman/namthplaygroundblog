#-*- coding: utf-8 -*-

# gcp storage
from google.oauth2 import service_account
from google.cloud import storage

# type hint
from google.cloud.storage import Client, Blob
from typing import List

# progress bar
from tqdm import tqdm

# file type
import mimetypes

# file path, env
import os

class Storage:
    def __init__(self):
        self.local_base_path = os.getenv("local_base_path")
        self.storage_base_path = os.getenv("storage_base_path")
        self.len_base_path = len(self.storage_base_path) + 1
        self.client = self._load_cred()
        self.bucket = self.client.get_bucket(os.getenv("gooogle_bucket_name"))

    # 인증정보 로딩
    def _load_cred(self) -> Client:
        key_path = os.getenv("google_cred_path")
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        return storage.Client(credentials=credentials, project=credentials.project_id)


    # content_type 설정
    def _get_content_type(self, source_url: str) -> str:
        return mimetypes.guess_type(source_url)[0]


    def _del_storage(self, job_info: dict):
        del_list = job_info["del_list"]
        print(f"DELETE STORAGE START(total : {len(del_list)})")
        pbar = tqdm(del_list)
        for del_f_path in pbar:
            blob_name = f"{self.storage_base_path}/{del_f_path}"
            blob = self.bucket.get_blob(blob_name)
            # each file progress bar
            pbar.set_description(f"deleting {blob_name}")
            # storage file delete
            blob.delete()
        pbar.close()
    
    def _upload_files(self, job_info: dict):
        upload_list = job_info["add_list"]
        print(f"UPLOAD START(total : {len(upload_list)})")
        pbar = tqdm(upload_list)
        for upload_f_path in pbar:
            blob_name = f"{self.storage_base_path}/{upload_f_path}"
            mime = self._get_content_type(upload_f_path)
            local_full_path = f"{self.local_base_path}/{upload_f_path}"
            blob = self.bucket.blob(blob_name)
            CACHE_CONTROL = "no-store"
            blob.cache_control = CACHE_CONTROL
            # each file progress bar
            pbar.set_description(f"uploading {local_full_path}")
            # file upload
            with open(local_full_path, "rb") as f:
                blob.upload_from_file(f, content_type=mime)
        pbar.close()
            


    def _download_files(self, job_info: dict):
        download_list = job_info["add_list"]
        storage_base_path = self.storage_base_path
        local_base_path = self.local_base_path
        print(f"DOWNLOAD START(total : {len(download_list)})")
        pbar = tqdm(download_list)
        for download_f_path in pbar:
            local_full_path = f"{local_base_path}/{download_f_path}"
            mime = self._get_content_type(download_f_path)
            blob_name = f"{storage_base_path}/{download_f_path}"
            blob = self.bucket.blob(blob_name)
            # each file progress bar
            pbar.set_description(f"downloading {blob_name}")
            # file download
            with open(local_full_path, "wb") as f:
                self.client.download_blob_to_file(blob, f)
        pbar.close()


    def _del_local(self, job_info: dict):
        del_list = job_info["del_list"]
        base_path = self.local_base_path
        print(f"DELETE LOCAL START(total : {len(del_list)})")
        pbar = tqdm(del_list)
        for del_f_path in pbar:
            full_path = f"{base_path}/{del_f_path}"
            # each file progress bar
            pbar.set_description(f"deleting {full_path}")
            # local file delete
            if(os.path.exists(full_path) and os.path.isfile(full_path)):
                os.remove(full_path)
        pbar.close()


    def get_file_list(self, target: str) -> List[str]:
        target_path = f"{self.storage_base_path}/{target}"
        file_list = list()
        blobs: List[Blob] = list(self.bucket.list_blobs(prefix=target_path))
        for blob in blobs:
            f_name = blob.name[self.len_base_path:]
            if(f_name != ""):
                file_list.append(f_name)
        return file_list
    
    def run(self, focus: str, job_info: dict):
        if(focus == "storage"):
            self._del_local(job_info)
            self._download_files(job_info)
        elif(focus == "local"):
            self._del_storage(job_info)
            self._upload_files(job_info)

if(__name__ == "__main__"):
    storage_tree = Storage()
    print(storage_tree.get_file_list("targetdir"))
    
