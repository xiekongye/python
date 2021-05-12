import cv2

if __name__ == '__main__':
    # 读取数据并灰度化
    ori_bg = cv2.imread('2579bf38ce2b96ba49781cfb2eeb3c8c_bg.jpg')
    ori_front = cv2.imread('2579bf38ce2b96ba49781cfb2eeb3c8c_fg.png')
    print(ori_bg.shape)
    bg = cv2.cvtColor(ori_bg, cv2.COLOR_BGR2GRAY)
    front = cv2.cvtColor(ori_front, cv2.COLOR_BGR2GRAY)

    # 寻找前景图的轮廓和位置
    contours, hierarchy = cv2.findContours(front, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    x, y, w, h = cv2.boundingRect(contour)
    print("the contour of front image is %s,%s,%s,%s" % (x, y, w, h))
    print("the height interval of front image is %s,%s" % (y, y + h))

    # 对前景图进行截取，只保留有内容的部分
    target = front[front.any(1)]
    print(target.shape)
    h, w = target.shape[:2]
    print("height of target image: ", h)
    print("weigth of target image: ", w)

    # 图像匹配
    res = cv2.matchTemplate(bg, target, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    x_interval = (min_loc[0], min_loc[0] + w)  # 横轴范围
    y_interval = (min_loc[1], min_loc[1] + h)  # 纵轴范围
    left_top = (x_interval[0], y_interval[0])
    right_bottom = (x_interval[1], y_interval[1])

    print("x_interval: [%s,%s]" % x_interval)
    print("y_interval:[%s,%s]" % y_interval)
    cv2.rectangle(bg, left_top, right_bottom, 255, 2)  # 画出矩形位置

    cv2.imwrite('aa1.png', bg)
    cv2.imwrite("aa2.png", front)