import pymysql
import time


def connect_review_db():
    return pymysql.connect(host='172.22.5.7',
                           port=3306,
                           user='',
                           password='',
                           database='')


if __name__ == '__main__':
    conn = connect_review_db()
    cur = conn.cursor()

    while 1:
        cur.execute("update customer_reviews153 set status=5, comment='更新为5' where review_id=176456250941268249")
        conn.commit()
        print('Update status to --> 5')
        cur.execute("update customer_reviews153 set status=2, comment='更新为2' where review_id=176456250941268249")
        print('Update status to --> 2')
        conn.commit()
        # time.sleep(0.5)