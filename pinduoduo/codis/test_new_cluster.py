# 测试新集群

import redis

old_cluster_url = 'localhost'
old_cluster_port = 6379
new_cluster_url = 'st1-hutaojie-cdp-1.prod.yiran.com'
new_cluster_port = 19000
# 仅有追评
only_append_goods_label_key_pattern = 'review_hive:v3:goods_id_hive:{0}:label_id_hive:{1}'
# 有追评，切有图
with_picture_append_goods_label_key_pattern = 'review:picture:v3:goods_id:{0}:label_id:{1}'


def get_redis_client(host, port):
    pool = get_redis_pool(host, port)
    return redis.Redis(connection_pool=pool)


def get_redis_pool(host, port):
    return redis.ConnectionPool(host=host, port=port)


def start():
    old_redis_cli = get_redis_client(old_cluster_url, old_cluster_port)
    new_redis_cli = get_redis_client(new_cluster_url, new_cluster_port)
    f = open('goods_id.txt', 'r')
    for line in f.readlines():
        old_val = old_redis_cli.get('goods_id:%s:%s' % (line, 1))
        new_val = new_redis_cli.get('goods_id:%s:%s' % (line, 1))
        print('old:%s' % old_val)
        print('new:%s' % new_val)
        if old_val == new_val:
            print('Equal')
    test_case_goods()


def mock():
    old_redis_cli = get_redis_client(old_cluster_url, old_cluster_port)
    new_redis_cli = get_redis_client(new_cluster_url, new_cluster_port)
    f = open('goods_id.txt', 'r')
    for line in f.readlines():
        old_redis_cli.set('goods_id:%s:%s' % (line, 1), 1)
        new_redis_cli.set('goods_id:%s:%s' % (line, 1), 1)


def test_case_goods():
    old_redis_cli = get_redis_client(old_cluster_url, old_cluster_port)
    new_redis_cli = get_redis_client(new_cluster_url, new_cluster_port)
    only_picture_set = new_redis_cli.zrange('review_hive:v3:goods_id_hive:{0}:label_id_hive:{1}'
                                            .format('24857', '100000000'), 0, -1)
    print(only_picture_set)
    for val in only_picture_set:
        print(val)

    label_count_set = new_redis_cli.zrevrange('label_hive:goods_id_hive:{0}'.format('24857'), 0, 200)
    print('label_count : {0}'.format(label_count_set))
    for label in label_count_set:
        print('Label : {0}, Score : {1}'.format(label, new_redis_cli.zscore('label_hive:goods_id_hive:{0}'.format('24857'), label)))


if __name__ == '__main__':
    mock()
    start()
