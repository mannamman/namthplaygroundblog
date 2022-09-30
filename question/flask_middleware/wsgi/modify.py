from werkzeug.wrappers import Request, Response
import json
import io

class ModifyPostBody:
    def __init__(self, app) -> None:
        self.app = app
    
    def __call__(self, environ: dict, start_response):
        # request = environ["werkzeug.request"]
        request = Request(environ)
        if(request.method == "POST"):
            # 기존의 body 읽어오기
            content_length = int(environ["CONTENT_LENGTH"])
            row_body: io.BufferedReader = environ['wsgi.input']
            body = row_body.read(content_length).decode("utf-8")
            # 새로운 body 작성
            new_body = json.dumps({
                "old_body": body,
                "new_body": {
                    "hello": "world!"
                }
            }).encode("utf-8")
            # 새로 작성한 body를 environ에 다시 넣기
            # CONTENT_LENGTH를 수정하지 않는다면 제대로 body가 들어가지 않음
            new_body_length = len(new_body)
            environ["CONTENT_LENGTH"] = new_body_length
            environ['wsgi.input'] = io.BytesIO(new_body)
        return self.app(environ, start_response)


class ModifyMethod:
    def __init__(self, app) -> None:
        self.app = app
    
    def __call__(self, environ: dict, start_response):
        method = environ["REQUEST_METHOD"]
        if(method == "PUT"):
            environ["REQUEST_METHOD"] = "POST"
        elif(method == "PATCH"):
            environ["REQUEST_METHOD"] = "GET"
        return self.app(environ, start_response)