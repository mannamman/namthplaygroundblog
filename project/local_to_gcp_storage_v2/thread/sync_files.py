#-*- coding: utf-8 -*-
# type hint
from typing import List, Tuple
# file worker
from file_worker import Worker
# thread
from threading import Thread
from tqdm import tqdm
from math import ceil


def make_chunk(files :List[str], file_cnt :int, chunk_size :int) -> List[List[str]]:
    return list(
        map(
            lambda x: files[x*chunk_size:x*chunk_size+chunk_size],
            [i for i in range(ceil(file_cnt/chunk_size))]
        )
    )

class Sync:
    def __init__(self, focus: str, target: str, ignore: List[str], overwrite: str):
        self.focus = focus
        self.overwrite = overwrite
        self.target = target

        self.file_worker = Worker(ignore=ignore)

        self.storage_file_list, self.local_file_list = self.file_worker.get_file_list(target)

        self.chunk_size = 5

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

        add_files_chunk = make_chunk(add_list, len(add_list), self.chunk_size)
        del_files_chunk = make_chunk(del_list, len(del_list), self.chunk_size)

        add_files_tqdm = tqdm(add_list)
        del_files_tqdm = tqdm(del_list)

        add_files_tqdm.set_description("ADD FILES")
        del_files_tqdm.set_description("DLETE FILES")
        
        threads: List[Thread] = []

        thread_idx = 1

        if(self.focus == "storage"):
            del_target = self.file_worker.delete_local_files
            add_target = self.file_worker.download_files
        elif(self.focus == "local"):
            del_target = self.file_worker.delete_storage_files
            add_target = self.file_worker.upload_files

        for del_chunk in del_files_chunk:
            thread = Thread(
                target=del_target,
                args=(thread_idx, del_chunk, del_files_tqdm)
            )
            thread_idx += 1
            threads.append(thread)

        for add_chunk in add_files_chunk:
            thread = Thread(
                target=add_target,
                args=(thread_idx, add_chunk, add_files_tqdm)
            )
            thread_idx += 1
            threads.append(thread)

        add_files_tqdm.write(f"UPLOAD START(total : {len(add_list)})")
        del_files_tqdm.write(f"DELETE START(total : {len(del_list)})")

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        
        add_files_tqdm.close()
        del_files_tqdm.close()

if(__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv()
    sync = Sync("local", "", True)
    sync.sync()


