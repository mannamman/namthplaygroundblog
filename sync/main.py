#-*- coding: utf-8 -*-
# main module
from sync_files import Sync
# user input
import argparse
# check running time
import time
# load .env file
from dotenv import load_dotenv
# .env file data to environment variable
load_dotenv()

parser = argparse.ArgumentParser(
    description="스토리지에있는 템플릿 코드와 로컬에있는 템플릿 코드를 쉽게 동기화하기 위한 함수"
)

parser.add_argument(
    "--focus", required=True, choices=["local", "storage"],
    help="동기화의 중점을 선택합니다."
)

parser.add_argument(
    "--target", required=False, default="",
    help="동기화할 목표를(폴더, 파일) 설정합니다. 입력하지 않을 시('') 현재 디렉토리 기준으로 실행됩니다."
)

parser.add_argument(
    "--ignore", required=False, default=None, nargs='+',
    help="동기화를 하지않을 파일 혹은 폴더를 지정합니다."
)

args = parser.parse_args()

if(__name__ == "__main__"):
    start = time.time()
    syncer = Sync(args.focus, args.target, args.ignore)
    syncer.sync()
    print(f"Sync done ...\nrunning time: {round((time.time() - start), 2)} sec")
