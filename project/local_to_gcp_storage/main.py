#-*- coding: utf-8 -*-
from sync_files import Sync
import argparse
import time

from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser(
    description="스토리지에있는 템플릿 코드와 로컬에있는 템플릿 코드를 쉽게 동기화하기 위한 함수"
)

parser.add_argument(
    "--focus_local", default=False, action="store_true",
    help="동기화의 중점을 선택합니다. True : Local, False : storage"
)

parser.add_argument(
    "--target", required=False, default="",
    help="동기화할 목표를(폴더, 파일) 설정합니다. '.'을 입력시 실행 디렉토리를 기준으로 동기화를 합니다."
)

parser.add_argument(
    "--overwrite", default=False, action="store_true",
    help="업로드, 다운로드시 이미 있는 파일을 덮어씌울지를 결정합니다. True : 덮어쓰기, False : 덮어쓰지 않음"
)

args = parser.parse_args()


if(__name__ == "__main__"):
    start = time.time()

    if(args.focus_local == False):
        weight = "storage"
    else:
        weight = "local"

    Sync(weight, args.target, args.overwrite).sync()
    print(f"sync done ...\nrunning time : {round((time.time() - start), 2)}")
