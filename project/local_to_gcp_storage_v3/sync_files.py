#-*- coding: utf-8 -*-
# type hint
from typing import List, Tuple
# file worker
from file_worker import Worker
# thread
from threading import Thread
# progress bar
from tqdm import tqdm
#
from math import ceil

def make_chunk(files :List[str], file_cnt :int, chunk_size :int) -> List[List[str]]:
    return list(
        map(
            lambda x: files[x*chunk_size:x*chunk_size+chunk_size],
            [i for i in range(ceil(file_cnt/chunk_size))]
        )
    )

class Sync:
    def __init__(self, focus: str, target: str, ignore: List[str]):
        self.focus = focus
        self.target = target

        self.file_worker = Worker(ignore=ignore)

        self.storage_file_list, self.local_file_list = self.file_worker.get_file_list(target)

        self.chunk_size = 5

    def _get_add_del_list(self) -> Tuple[List[str], List[str]]:
        local_hash = self.file_worker.get_local_hash(self.local_file_list)
        storage_hash = self.file_worker.get_storage_hash(self.storage_file_list)

        add_list = []
        del_list = []

        if(self.focus == "storage"):
            # 로컬을 지우고, 스토리지 -> 로컬 다운로드
            for storage_file in storage_hash:
                if(storage_file  in local_hash):
                    if(storage_hash[storage_file] == local_hash[storage_file]):
                        continue
                    else:
                        add_list.append(storage_file)
                else:
                    add_list.append(storage_file)
            for local_file in local_hash:
                if(local_file not in storage_hash):
                    del_list.append(local_file)
        else:
            # 스토리지를 지우고, 로컬 -> 스토리지 업로드
            for local_file in local_hash:
                if(local_file  in storage_hash):
                    if(local_hash[local_file] == storage_hash[local_file]):
                        continue
                    else:
                        add_list.append(local_file)
                else:
                    add_list.append(local_file)
            for storage_file in storage_hash:
                if(storage_file not in local_hash):
                    del_list.append(storage_file)

        return add_list, del_list

    def sync(self):
        # 누락된 파일, 변경된 파일 검사
        add_list, del_list = self._get_add_del_list()

        # 1차원 배열 -> 2차원 배열
        add_files_chunk = make_chunk(add_list, len(add_list), self.chunk_size)
        del_files_chunk = make_chunk(del_list, len(del_list), self.chunk_size)

        # 프로그레스 바 출력을 위한 tqdm 객체 생성(파일 추가, 삭제 각각 1개)
        add_files_tqdm = tqdm(add_list)
        del_files_tqdm = tqdm(del_list)

        # 프로그레스 바 설명 추가
        add_files_tqdm.set_description("ADD FILES")
        del_files_tqdm.set_description("DLETE FILES")
        
        # 쓰레드를 담을 배열 생성 및 쓰레드별 id가될 변수 초기화
        threads: List[Thread] = []
        thread_idx = 1

        # 쓰레드별 타깃함수 설정
        if(self.focus == "storage"):
            del_target = self.file_worker.delete_local_files
            add_target = self.file_worker.download_files
        elif(self.focus == "local"):
            del_target = self.file_worker.delete_storage_files
            add_target = self.file_worker.upload_files

        # 쓰레드 초기화 및 배열에 넣기
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

        # 작업 개요 출력
        add_files_tqdm.write(f"UPLOAD START(total : {len(add_list)})")
        del_files_tqdm.write(f"DELETE START(total : {len(del_list)})")

        # 쓰레드 실행
        for thread in threads:
            thread.start()

        # 남은 쓰레드를 대기
        for thread in threads:
            thread.join()
        
        # tqdm 객체 닫기
        add_files_tqdm.close()
        del_files_tqdm.close()

if(__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv()
    sync = Sync("local", "", None, True)
