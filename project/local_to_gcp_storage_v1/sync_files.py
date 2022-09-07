#-*- coding: utf-8 -*-

# type hint
from typing import List, Tuple

# storage module
from gcp_storage import Storage

# local file module
from local_file import LocalFile

class Sync:
    def __init__(self, focus: str, target: str, overwrite: str):
        self.focus = focus
        self.overwrite = overwrite
        self.target = target

        self.storage_worker = Storage()
        self.local_worker = LocalFile()

        self.storage_file_list = self.storage_worker.get_file_list(target)
        self.local_file_list = self.local_worker.get_file_list(target)


    def list_print(self):
        print(self.local_file_list)
        print("=" * 30)
        print(self.storage_file_list)

    def sync(self):

        if(self.focus == "storage"):
            # 로컬을 지우고, 스토리지 -> 로컬 다운로드
            add_list, del_list = self._storage_to_local()
        else:
            # 스토리지를 지우고, 로컬 -> 스토리지 업로드
            add_list, del_list = self._local_to_stroage()

        job_info = {
            "focus" : self.focus,
            "target": self.target,
            "add_list" : add_list,
            "del_list" : del_list
        }
        self.storage_worker.run(self.focus, job_info)


    def _local_to_stroage(self) -> Tuple[List[str], List[str]]:
        """
        focus == local
        로컬을 기준으로 동기화(로컬 -> 스토리지)
        """
        # del_list는 스토리지에서 삭제할 목록
        del_list = [del_e for del_e in self.storage_file_list if del_e not in self.local_file_list]

        # add_list는 로컬에서 스토리지로 업로드 할 목록
        # 덮어쓰기가 true면 로컬의 전부를 스토리지로 옮겨야함
        if(self.overwrite):
            add_list = self.local_file_list
        else:
            add_list = [add_e for add_e in self.local_file_list if add_e not in self.storage_file_list]
        return add_list, del_list


    def _storage_to_local(self) -> Tuple[List[str], List[str]]:
        """
        focus == storage
        스토리지를 기준으로 동기화(스토리지 -> 로컬)
        """
        # del_list는 로컬에서 삭제할 파일 목록
        del_list = [del_e for del_e in self.local_file_list if del_e not in self.storage_file_list]

        # add_list는 스토리지에서 로컬로 다운로드 할 목록
        # 덮어쓰기가 true면 스토리지의 파일을 전부 로컬로 옮겨야함
        if(self.overwrite):
            add_list = self.storage_file_list
        else:
            add_list = [add_e for add_e in self.storage_file_list if add_e not in self.local_file_list]
        return add_list, del_list


if(__name__ == "__main__"):
    sync = Sync("local", "", True)
    sync.sync()