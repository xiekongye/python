# -*- coding: UTF-8 -*-
from __future__ import print_function

import mysql.connector


def update_shard_table():
    cnx = mysql.connector.connect(host='172.22.5.7', user='review_rw', password='review2018')
    cursor = cnx.cursor()

    sql = '''
    alter table `review_extension%s` add `video` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '是否带视频，0：否，1：是';
    '''

    for i in range(1):
        cursor.execute('use pdd_review;')

        for j in range(512):
            try:
                cursor.execute(sql, (j,))
                print("update table {} success!".format("{}{}".format("review_extension", j)))
            except mysql.connector.Error as err:
                print(err.msg)

    cnx.commit()
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    update_shard_table()
