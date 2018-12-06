# -*- coding: UTF-8 -*-
from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode


def create_shard_table():
    cnx = mysql.connector.connect(host='', port='', user='', password='')
    cursor = cnx.cursor()

    # 建库语句
    create_db_sql = '''
    CREATE DATABASE `test_shard%s`;
    '''

    # 建表语句
    create_table_sql = '''
    CREATE TABLE `person%s` (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id主键',
      `name` varchar(100) NOT NULL DEFAULT '' COMMENT '姓名',
      `age` tinyint(3) NOT NULL DEFAULT '0' COMMENT '年龄',
      `gender` char(10) NOT NULL DEFAULT 'male' COMMENT '性别(男性：male，女性：female)',
      PRIMARY KEY (`id`),
      UNIQUE KEY `person1_id_uindex` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    '''

    for i in range(4):
        cursor.execute(create_db_sql, (i,))
        cursor.execute('use {};'.format('test_shard{}'.format(i)))

        for j in range(4):
            try:
                cursor.execute(create_table_sql, (j,))
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
