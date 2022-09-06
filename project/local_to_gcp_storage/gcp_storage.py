#-*- coding: utf-8 -*-
"""
스토리지의 파일들의 리스트를 불러오는 함수
"""
from typing import Dict, List
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.storage import Client, Blob, Bucket
from google.cloud.exceptions import NotFound as blob_not_found
import os
from dotenv import load_dotenv
import mimetypes
from tqdm import tqdm

load_dotenv()

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
            blob.delete()
            pbar.set_description(f"deleteing {blob_name}")
    
    def _upload_files(self, job_info: dict):
        upload_list = job_info["add_list"]
        print(f"UPLOAD START(total : {len(upload_list)})")
        pbar = tqdm(upload_list)
        for upload_f_path in pbar:
            blob_name = f"{self.storage_base_path}/{upload_f_path}"
            mime = self._get_content_type(upload_f_path)
            local_full_path = f"{self.local_base_path}/{upload_f_path}"
            blob = self.bucket.blob(blob_name)
            ## cache contorl ##
            # CACHE_CONTROL = "public, max-age=30"
            CACHE_CONTROL = "no-store"
            blob.cache_control = CACHE_CONTROL
            with open(local_full_path, "rb") as f:
                blob.upload_from_file(f, content_type=mime)
            pbar.set_description(f"uploading {local_full_path}")


    def _download_files(self, job_info: dict):
        download_list = job_info["add_list"]
        storage_base_path = job_info["storage_base_path"]
        local_base_path = job_info["local_base_path"]
        print(f"DOWNLOAD START(total : {len(download_list)})")
        pbar = tqdm(download_list)
        for download_f_path in pbar:
            local_full_path = f"{local_base_path}{download_f_path}"
            mime = self._get_content_type(download_f_path)
            blob_name = f"{storage_base_path}{download_f_path}"
            blob = self.bucket.blob(blob_name)
            print("downloads", blob_name)
            with open(local_full_path, "wb") as f:
                self.client.download_blob_to_file(blob, f)
            pbar.set_description(f"downloading {blob_name}")

    def _del_local(self, job_info: dict):
        del_list = job_info["del_list"]
        base_path = job_info["local_base_path"]
        print(f"DELETE LOCAL START(total : {len(del_list)})")
        pbar = tqdm(del_list)
        for del_f_path in pbar:
            full_path = f"{base_path}{del_f_path}"
            if(os.path.exists(full_path) and os.path.isfile(full_path)):
                os.remove(full_path)
            pbar.set_description(f"deleteing {full_path}")


    def get_file_list(self, target: str) -> List[str]:
        target_path = f"{self.storage_base_path}/{target}"

        file_list = list()
        blobs: List[Blob] = list(self.bucket.list_blobs(prefix=target_path))
        for blob in blobs:
            f_name = blob.name[self.len_base_path:]
            if(f_name != ""):
                file_list.append(f_name)
        return file_list
    
    def run(self, weight: str, job_info: dict):
        if(weight == "stroage"):
            self._del_local(job_info)
            self._download_files(job_info)
        elif(weight == "local"):
            self._del_storage(job_info)
            self._upload_files(job_info)

if(__name__ == "__main__"):
    # storage_tree = StorageFileTree("aiso_template", ".")
    storage_tree = Storage()
    print(storage_tree.get_file_list("tf"))
    
