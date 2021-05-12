import datetime
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import cv2
import redis
import urllib

import mitmproxy
from mitmproxy.script import concurrent

mock_img_url = ''
mock_gif_url = ''
mock_video_url = ''

# 滑块请求
slider_path_pattern = '/ca/v1/register'

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
    "/api/sns/v6/homefeed", #首页
    "/ca/v1/register" #滑块
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
        self.redis = redis.StrictRedis(host='localhost', port=6379)

    @concurrent
    def request(self, flow: mitmproxy.http.HTTPFlow):
        print('*******************收到请求*******************')
        print(flow.request.pretty_url + '\n')

    @concurrent
    def response(self, flow: mitmproxy.http.HTTPFlow):
        url = flow.request.pretty_url
        url_res = urlparse(url)
        path = url_res.path

        for k, v in flow.response.headers.items():
            print("%-20s: %s" % (k.upper(), v))

        for url_patten in xhs_url_white_pattern:
            if re.match(url_patten, path):
                print('*******************处理合法响应*******************')
                print('url pattern: {}\nurl: {}'.format(url_patten, url))

                # 处理滑块请求
                if slider_path_pattern == url_patten:
                    resp = flow.response.text
                    resp_json = resp[resp.find('{'): resp.rfind('}') + 1]
                    print('开始处理滑块请求，滑块url: {}，响应：{}，截取json：{}'.format(url, resp, resp_json))
                    slider_resp = json.loads(resp_json)
                    fg_url = 'https://castatic.fengkongcloud.com' + slider_resp['detail']['fg']
                    bg_url = 'https://castatic.fengkongcloud.com' + slider_resp['detail']['bg']

                    fg_info = get_image_id_and_format(fg_url)
                    fg_id = fg_info[0]
                    fg_format = fg_info[1]

                    bg_info = get_image_id_and_format(bg_url)
                    bg_id = bg_info[0]
                    bg_format = bg_info[1]

                    print('滑块前景图url：{}，前景图Id：{}\n背景图url：{}，背景图id：{}'.format(fg_url, fg_id, bg_url, bg_id))

                    file_root_path = '/xhs/sliderimage/tmp/'
                    fg_file_path = (file_root_path + '{}.{}').format(fg_id, fg_format)
                    # fg_render_file_path = (file_root_path + '{}_render.{}').format(fg_id, fg_format)
                    bg_file_path = (file_root_path + '{}.{}').format(bg_id, bg_format)
                    # bg_render_file_path = (file_root_path + '{}_render.{}').format(bg_id, bg_format)
                    download_file(fg_url, file_root_path, fg_file_path)
                    download_file(bg_url, file_root_path, bg_file_path)

                    # 写入redis
                    # detect_info = slider_detect(fg_file_path, fg_render_file_path, bg_file_path, bg_render_file_path)
                    detect_info = slider_detect_v2(bg_file_path, fg_file_path)
                    redis_key = fg_id + '|' + bg_id
                    self.redis.hmset(redis_key, detect_info)
                    print('滑块处理信息写入redis成功，redis key：{}\n检测结果：{}'.format(redis_key, detect_info))
                    return

                now = datetime.datetime.now()
                request_obj = {}
                request_obj["pretty_url"] = str(url)
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
                    return

                img_filter(response_body_json)

                flow.response.content = bytes(json.dumps(response_body_json), encoding="utf8")
                break


def write_file(file_name, file_content):
    addsource2content(file_content)
    with open(file_name, "a") as ofile:
        ofile.write(json.dumps(file_content) + "\n")

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径

def addsource2content(flow_obj):
    try:
        content_obj = json.loads(flow_obj["response"]["content"])
    except:
        pass
    content_obj["loadsource"] = "user"

    flow_obj["response"]["content"] = json.dumps(content_obj)
    return flow_obj

def slider_detect(fg_path, fg_render_file_path, bg_path, bg_render_file_path):
    # 读取数据并灰度化
    ori_bg = cv2.imread(bg_path)
    ori_front = cv2.imread(fg_path)
    print(ori_bg.shape)
    bg = cv2.cvtColor(ori_bg, cv2.COLOR_BGR2GRAY)
    front = cv2.cvtColor(ori_front, cv2.COLOR_BGR2GRAY)

    # 寻找前景图的轮廓和位置
    fg_contours, fg_hierarchy = cv2.findContours(front, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    fg_contour = fg_contours[0]
    fg_x, fg_y, fg_w, fg_h = cv2.boundingRect(fg_contour)

    # 背景图长宽位置
    bg_contours, bg_hierarchy = cv2.findContours(bg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bg_contour = bg_contours[0]
    bg_x, bg_y, bg_w, bg_h = cv2.boundingRect(bg_contour)

    # 对前景图进行截取，只保留有内容的部分
    target = front[front.any(1)]
    print(target.shape)
    fg_h, fg_w = target.shape[:2]
    print("height of target image: ", fg_h)
    print("weigth of target image: ", fg_w)

    # 图像匹配
    res = cv2.matchTemplate(bg, target, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    x_interval = (min_loc[0], min_loc[0] + fg_w)  # 横轴范围
    y_interval = (min_loc[1], min_loc[1] + fg_h)  # 纵轴范围
    left_top = (x_interval[0], y_interval[0])
    right_bottom = (x_interval[1], y_interval[1])

    print("x_interval: [%s,%s]" % x_interval)
    print("y_interval: [%s,%s]" % y_interval)
    cv2.rectangle(bg, left_top, right_bottom, 255, 2)  # 画出矩形位置

    cv2.imwrite(bg_render_file_path, bg)
    cv2.imwrite(fg_render_file_path, front)

    detect_info = {}
    detect_info['fg_width'] = fg_w
    detect_info['fg_height'] = fg_h
    detect_info['bg_width'] = bg_w
    detect_info['bg_height'] = bg_h
    detect_info['x_loc'] = x_interval[0]
    detect_info['y_loc'] = y_interval[0]
    return detect_info


def slider_detect_v2(bg_pic, fg_pic):
    '''
    滑块检测第二版
    :param bg_pic: 背景图图片url
    :param fg_pic: 前景图图片url
    :return: 检测结果
    '''
    # 读取数据
    ori_bg = cv2.imread(bg_pic)
    ori_front = cv2.imread(fg_pic)

    # 灰度化
    bg = cv2.cvtColor(ori_bg, cv2.COLOR_BGR2GRAY)
    front = cv2.cvtColor(ori_front, cv2.COLOR_BGR2GRAY)

    # 寻找target的轮廓
    fg_contours, hierarchy = cv2.findContours(front, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    fg_contour = fg_contours[0]
    # 输出前景图的坐标
    fg_x, fg_y, fg_w, fg_h = cv2.boundingRect(fg_contour)
    # print("the contour of front image is %s,%s,%s,%s" % (x, y, w, h))
    # print("the height interval of front image is %s,%s" % (y, y + h))
    # 截取前景图
    target2 = ori_front[fg_y:fg_y + fg_h, fg_x:fg_x + fg_w]

    # 背景图坐标获取
    bg_contours, hierarchy = cv2.findContours(bg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bg_contour = bg_contours[0]
    # 输出背景图的坐标
    bg_x, bg_y, bg_w, bg_h = cv2.boundingRect(bg_contour)

    # 进行匹配
    match_method = cv2.TM_CCOEFF_NORMED
    res = cv2.matchTemplate(ori_bg, target2, match_method)
    cv2.normalize(res, res, 0, 1, cv2.NORM_MINMAX, -1)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if (match_method == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED):
        matchLoc = min_loc
    else:
        matchLoc = max_loc

    # 确定识别结果的横纵坐标范围
    x_interval = (matchLoc[0], matchLoc[0] + fg_w)  # 横轴范围
    y_interval = (matchLoc[1], matchLoc[1] + fg_h)  # 纵轴范围
    # left_top = (x_interval[0], y_interval[0])  # 左上角
    # right_bottom = (x_interval[1], y_interval[1])  # 右下角

    # 输出识别结果的范围
    # print("x_interval: [%s,%s]" % x_interval)
    # print("y_interval:[%s,%s]" % y_interval)

    # 展示识别结果
    # img_display = ori_bg.copy()
    # cv2.rectangle(img_display, left_top, right_bottom, 255, 2)  # 画出矩形位置
    # target_url = "./result/" + name + "_target.png"
    # output_url = "./result/" + name + "_match.png"
    # cv2.imwrite(target_url, target2)
    # cv2.imwrite(output_url, img_display)

    detect_info = {}
    detect_info['fg_width'] = fg_w
    detect_info['fg_height'] = fg_h
    detect_info['bg_width'] = bg_w
    detect_info['bg_height'] = bg_h
    detect_info['x_loc'] = x_interval[0]
    detect_info['y_loc'] = y_interval[0]
    return detect_info

# 文件下载
def download_file(url, file_path, file_name):
    # 是否有这个路径
    if not os.path.exists(file_path):
        # 创建路径
        os.makedirs(file_path)

    print('开始下载图片到本地，url：{}，文件完整路径：{}'.format(url, file_name))
    urllib.request.urlretrieve(url, filename=file_name)

# 获取图片的唯一Id，需要存储到redis中
def get_image_id_and_format(image_url):
    url_res = urlparse(image_url)
    path = url_res.path
    path_arr = path.split('/')
    return path_arr[-1].split('.')


addons = [
    ResponseProxy("mitmproxy8080")
]
