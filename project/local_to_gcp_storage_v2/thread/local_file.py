#-*- coding: utf-8 -*-
# type hint
from typing import List
# file path, env
import os
# path name matching
import glob

class LocalFile:
    def __init__(self, *args):
        # .git : 깃 폴더
        # venv: python 가상환경 폴더
        # node_modules: node 패키지 폴더
        self.ignores = [".git", "venv", "node_modules", ".env"]
        if(args):
            self.ignores.extend(*args)

        self.local_base_path = os.getenv("local_base_path")
        self.storage_base_path = os.getenv("storage_base_path")
        self.len_project_local_base_path = len(self.local_base_path) + 1

    def _get_file_list(self, cur_dir: str, file_list: List[str]) -> None:
        for f in glob.glob(f"{cur_dir}/**"):
            if(os.path.basename(f) in self.ignores):
                continue
            if(os.path.isdir(f)):
                self._get_file_list(f, file_list)
            else:
                file_list.append(f[self.len_project_local_base_path:])

    
    def get_file_list(self, target: str) -> List[str]:
        target_path = f"{self.local_base_path}/{target}"

        file_list = list()
        if(os.path.isfile(target_path)):
            return [target_path]
        self._get_file_list(target_path, file_list)

        return file_list

if(__name__ == "__main__"):
    local_tree = LocalFile(["foo.bar.txt"])
    local_tree.get_file_list("project")
