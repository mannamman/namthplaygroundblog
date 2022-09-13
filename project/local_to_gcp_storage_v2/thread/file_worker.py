#-*- coding: utf-8 -*-
# gcp storage
from google.oauth2 import service_account
from google.cloud import storage
# type hint
from google.cloud.storage import Client, Blob
from typing import List, Tuple
# progress bar
from tqdm import tqdm
# file type
import mimetypes
# file path, env
import os
# decorator
import functools
# path name matching
import glob

def pbar_manager(func):
    @functools.wraps(func)
    def wrapper(*args):
        file_list = args[2]
        pbar = tqdm(file_list)
        func(*args, pbar)
        pbar.close()
        return
    return wrapper

class Worker:
    def __init__(self, ignore: List[str]):
        # ignore 설정
        self.ignores = [".git", "venv", "node_modules", ".env", "cred"]
        if(ignore):
            self.ignores.extend(ignore)
        # 로컬 경로 및 스토리지 경로 설정
        self.local_base_path = os.getenv("local_base_path")
        self.len_local_base_path = len(self.local_base_path) + 1
        self.storage_base_path = os.getenv("storage_base_path")
        self.len_storage_base_path = len(self.storage_base_path) + 1
        # 스토리지 객체 생성
        self.client = self._load_cred()
        self.bucket = self.client.get_bucket(os.getenv("gooogle_bucket_name"))

    # 인증정보 로드
    def _load_cred(self) -> Client:
        key_path = os.getenv("google_cred_path")
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        return storage.Client(credentials=credentials, project=credentials.project_id)


    # content_type 설정
    def _get_content_type(self, source_url: str) -> str:
        return mimetypes.guess_type(source_url)[0]


    @pbar_manager
    def delete_storage_files(self, thread_idx, file_list: List[str], pbar: tqdm):
        pbar.write(f"{thread_idx} DELETE STORAGE START(total : {len(file_list)})")
        for del_f_path in pbar:
            blob_name = f"{self.storage_base_path}/{del_f_path}"
            blob = self.bucket.get_blob(blob_name)
            pbar.set_description(f"{thread_idx} DELETING {blob_name}")
            blob.delete()
        pbar.write(f"{thread_idx} DELETE STORAGE DONE(total : {len(file_list)})")
    
    @pbar_manager
    def upload_files(self, thread_idx, file_list: List[str], pbar: tqdm):
        pbar.write(f"{thread_idx} UPLOAD START(total : {len(file_list)})")
        for upload_f_path in pbar:
            blob_name = f"{self.storage_base_path}/{upload_f_path}"
            mime = self._get_content_type(upload_f_path)
            local_full_path = f"{self.local_base_path}/{upload_f_path}"
            blob = self.bucket.blob(blob_name)
            CACHE_CONTROL = "no-store"
            blob.cache_control = CACHE_CONTROL
            pbar.set_description(f"{thread_idx} UPLOADING {local_full_path}")
            with open(local_full_path, "rb") as f:
                blob.upload_from_file(f, content_type=mime)
            
        pbar.write(f"{thread_idx} UPLOAD DONE(total : {len(file_list)})")
            

    @pbar_manager
    def download_files(self, thread_idx, file_list: List[str], pbar: tqdm):
        storage_base_path = self.storage_base_path
        local_base_path = self.local_base_path
        pbar.write(f"{thread_idx} DOWNLOAD START(total : {len(file_list)})")
        for download_f_path in pbar:
            local_full_path = f"{local_base_path}/{download_f_path}"
            blob_name = f"{storage_base_path}/{download_f_path}"
            blob = self.bucket.blob(blob_name)
            pbar.set_description(f"{thread_idx} DOWNLOADING {blob_name}")
            with open(local_full_path, "wb") as f:
                self.client.download_blob_to_file(blob, f)
        
        pbar.write(f"{thread_idx} DOWNLOAD DONE(total : {len(file_list)})")

    @pbar_manager
    def delete_local_files(self, thread_idx, file_list: List[str], pbar: tqdm):
        base_path = self.local_base_path
        pbar.write(f"{thread_idx} DELETE LOCAL START(total : {len(file_list)})")
        for del_f_path in pbar:
            full_path = f"{base_path}/{del_f_path}"
            pbar.set_description(f"{thread_idx} DELETING {full_path}")
            if(os.path.exists(full_path) and os.path.isfile(full_path)):
                os.remove(full_path)
        pbar.write(f"{thread_idx} DELETE LOCAL DONE(total : {len(file_list)})")


    def _get_local_file_list(self, target: str, file_list: List[str]) -> List[str]:
        for f in glob.glob(f"{target}/**"):
            if(os.path.basename(f) in self.ignores):
                continue
            if(os.path.isdir(f)):
                self._get_local_file_list(f, file_list)
            else:
                file_list.append(f[self.len_local_base_path:])

    def _get_storage_file_list(self, target: str) -> List[str]:
        file_list = list()
        blobs: List[Blob] = list(self.bucket.list_blobs(prefix=target))
        for blob in blobs:
            f_name = blob.name[self.len_storage_base_path:]
            if(f_name != ""):
                file_list.append(f_name)
        return file_list

    def get_file_list(self, target: str) -> Tuple[List[str], List[str]]:
        # 스토리지 파일리스트 가져오기
        storage_target_path = f"{self.storage_base_path}/{target}"
        storage_file_list = self._get_storage_file_list(storage_target_path)

        # 로컬 파일리스트 가져오기
        local_target_path = f"{self.local_base_path}/{target}"
        local_file_list = list()
        if(os.path.isfile(local_target_path)):
            local_file_list = [local_target_path]
        self._get_local_file_list(local_target_path, local_file_list)

        return storage_file_list, local_file_list
        

if(__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv()
    worker = Worker()
    storage_file_list, local_file_list = worker.get_file_list("")
    print(storage_file_list)
    print(local_file_list)    
