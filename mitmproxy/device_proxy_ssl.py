import datetime
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import mitmproxy
from mitmproxy import ctx

mock_img_url = ''
mock_gif_url = ''
mock_video_url = ''

xhs_url_white_pattern = [
    "^/api/sns/v1/note/user/.+/videofeed",
    "^/api/sns/v1/note/.+/feed",
    "/api/sns/v2/note/.+/videofeed",
    "/api/sns/v10/search/notes",
    "/api/store/nb/bridge/cards",
    "/api/sns/v4/note/user/posted",
    "/api/sns/v3/user/.+/info",
    "/api/sns/v3/search/user",
    "/api/sns/v2/search/filter", #关键词搜索标签页
    "/api/sns/v6/homefeed" #首页
]


def img_filter(obj):
    if isinstance(obj, dict):
        for k in obj:
            val = obj[k]
            if val != None and isinstance(val, str):
                if val.endswith(".jpeg") \
                        or val.endswith(".jpg") \
                        or val.endswith(".png") \
                        or val.endswith(".SS2") \
                        or val.endswith('webp') \
                        or '-img-' in val:
                    if '-anim-' in val:
                        obj[k] = mock_gif_url
                    else:
                        obj[k] = mock_img_url
                elif val.endswith(".mp4") or '-video-' in val or val.endswith(".kpg"):
                    obj[k] = mock_video_url
            elif isinstance(obj[k], dict) or isinstance(obj[k], list):
                img_filter(obj[k])
    elif isinstance(obj, list):
        for x in range(len(obj)):
            if isinstance(obj[x], str):
                val = obj[x]
                if val != None:
                    if val.endswith(".jpeg") \
                            or val.endswith(".jpg") \
                            or val.endswith(".png") \
                            or val.endswith(".SS2") \
                            or val.endswith('webp') \
                            or '-img-' in val:
                        if '-anim-' in val:
                            obj[x] = mock_gif_url
                        else:
                            obj[x] = mock_img_url
                    elif val.endswith(".mp4") or '-video-' in val or val.endswith(".kpg"):
                        obj[x] = mock_video_url
            elif isinstance(obj[x], dict) or isinstance(obj[x], list):
                img_filter(obj[x])


class ResponseProxy:
    def __init__(self, dir):
        self.dir = dir
        self.executor = ThreadPoolExecutor(max_workers=100, thread_name_prefix='writefile2disk')

    def response(self, flow: mitmproxy.http.HTTPFlow):
        url = flow.request.pretty_url
        url_res = urlparse(url)
        path = url_res.path
        host = url_res.netloc

        for url_patten in xhs_url_white_pattern:
            if re.match(url_patten, path):
                ctx.log.info('匹配到url pattern: %s, url path: %s，原始url: %s' % (url_patten, path, url))
                now = datetime.datetime.now()
                request_obj = {}
                request_obj["pretty_url"] = str(flow.request.pretty_url)
                request_obj["headers"] = {}
                for k, v in flow.request.headers.items(True):
                    request_obj["headers"][k] = v

                request_body_str = flow.request.text
                if request_body_str:
                    request_obj["body"] = request_body_str
                elif flow.request.content:
                    try:
                        request_obj["body"] = flow.request.content.decode('utf-8')
                    except:
                        ctx.log.error("请求content无法decode，直接返回")
                        return
                else:
                    request_obj["body"] = ""

                response_obj = {}
                response_body_str = flow.response.text
                if response_body_str:
                    response_obj["content"] = response_body_str
                elif flow.response.content:
                    try:
                        response_obj["content"] = flow.response.content.decode('utf-8')
                    except:
                        ctx.log.error("响应response无法decode，直接返回")
                        return
                else:
                    response_obj["content"] = ""

                response_obj["status"] = flow.response.status_code
                flow_obj = {}
                flow_obj["request"] = request_obj
                flow_obj["response"] = response_obj
                flow_obj["time"] = now.strftime("%Y-%m-%d %H:%M:%S")

                dir_path = "/home/lieying/web/lilburne/adb/pull/" + now.strftime("%Y-%m-%d_%H") + "/" + self.dir
                file_name = dir_path + "/dump_" + now.strftime("%Y-%m-%d_%H") + ".txt"
                mkdir(dir_path)

                # 线程池处理文件存储
                self.executor.submit(write_file, file_name, flow_obj)

                try:
                    response_body_json = json.loads(response_body_str)
                except:
                    ctx.log.error("转换content实体异常：%s" % response_body_str)
                    return

                img_filter(response_body_json)

                flow.response.content = bytes(json.dumps(response_body_json), encoding="utf8")
                break


def write_file(file_name, file_content):
    with open(file_name, "a") as ofile:
        ofile.write(json.dumps(file_content) + "\n")

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径

addons = [
    ResponseProxy("mitmproxy")
]
