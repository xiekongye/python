# -*- coding: UTF-8 -*-
from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode


def create_shard_table():
    cnx = mysql.connector.connect(host='172.22.5.7', user='review_rw', password='review2018')
    cursor = cnx.cursor()

    sql = '''
    CREATE TABLE `review_video%s` (
      `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
      `review_id` bigint(20) unsigned NOT NULL COMMENT '原评论编号',
      `belong` tinyint(2) unsigned NOT NULL COMMENT '视频归属主评还是追评,0:主评,1:追评',
      `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '视频url链接',
      `width` int(10) unsigned NOT NULL COMMENT '视频宽度',
      `height` int(10) unsigned NOT NULL COMMENT '视频高度',
      `duration` tinyint(3) unsigned NOT NULL default '0' COMMENT '视频时长（单位：秒）',
      `size` bigint(20) unsigned NOT NULL default '0' COMMENT '视频大小（单位byte）',
      `handler` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '操作人编号',
      `status` int(10) unsigned NOT NULL DEFAULT '4' COMMENT '视频状态（同图片状态），0：正常， 4：初始化，5：被过滤',
      `cover_image_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '视频封面图片链接',
      `cover_image_width` int(10) unsigned NOT NULL COMMENT '视频封面图片宽度',
      `cover_image_height` int(10) unsigned NOT NULL COMMENT '视频封面图片高度',
      `cover_image_status` int(10) unsigned NOT NULL DEFAULT '4' COMMENT '视频封面图状态（同图片状态），0：正常， 4：初始化，5：被过滤',
      `created_at` int(10) unsigned NOT NULL COMMENT '创建时间',
      `updated_at` int(10) unsigned NOT NULL COMMENT '更新时间',
      `ext_1` int(11) NOT NULL DEFAULT '0' comment '备用字段int',
      `ext_2` int(11) NOT NULL DEFAULT '0' comment '备用字段int',
      `ext_3` bigint(20) NOT NULL DEFAULT '0' comment '备用字段 bigint',
      `ext_4` bigint(20) NOT NULL DEFAULT '0' comment '备用字段 bigint',
      `ext_a` varchar(255) NOT NULL DEFAULT '' comment '备用字段 varchar',
      `ext_b` varchar(255) NOT NULL DEFAULT '' comment '备用字段 varchar',
      PRIMARY KEY (`id`),
      KEY `created_at` (`created_at`) USING BTREE,
      KEY `updated_at` (`updated_at`) USING BTREE,
      KEY `review_id` (`review_id`) USING BTREE,
      KEY `belong` (`belong`) USING BTREE
    ) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='review video table'
    '''

    for i in range(1):
        cursor.execute('use pdd_review;')

        for j in range(512):
            try:
                cursor.execute(sql, (j,))
                print("create table {} success!".format("{}{}".format("review_video", j)))
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists {}_{}".format("review_video", i))
                else:
                    print(err.msg)

    cnx.commit()
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    create_shard_table()
