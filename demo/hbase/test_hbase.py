import hashlib


def md5(string_val):
    h5 = hashlib.md5()
    h5.update(string_val.encode(encoding='utf-8'))
    digest_val = h5.hexdigest()
    print('MD5加密前为 ：' + string_val)
    print('MD5加密后为 ：' + digest_val)
    return digest_val


def generateSortedReviewIdsRowKey(goods_id):
    return "%s-%019d".format()


if __name__ == '__main__':
    print(md5('xiekongye'))
