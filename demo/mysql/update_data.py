import pymysql
import time
import threading


def connect_review_db():
    return pymysql.connect(host='172.22.5.7',
                           port=3306,
                           user='service_tmp_0906',
                           password='passwdpasswd',
                           database='pdd_review')


def loop():
    conn = connect_review_db()
    cur = conn.cursor()

    while True:
        print("MainReview : ***************** \n")
        cur.execute("update customer_reviews153 set status=5, comment='更新为5' where review_id=176456250941268249")
        conn.commit()
        print('Update status to --> 5')
        cur.execute("update customer_reviews153 set status=2, comment='更新为2' where review_id=176456250941268249")
        print('Update status to --> 2')
        conn.commit()
        # time.sleep(2)


def illegal_loop():
    conn = connect_review_db()
    cur = conn.cursor()
    while True:
        print('Illegal')
        cur.execute("update review_pictures153 set status=0 where review_id=76950256065339673")
        conn.commit()
        cur.execute("update review_pictures153 set status=1 where review_id=76950256065339673")
        conn.commit()


if __name__ == '__main__':
    threading.Thread(target=loop, name='thread-0').start()
    # thread_list = [threading.Thread(target=loop, name='thread-0'),
    #                threading.Thread(target=illegal_loop, name='thread-1')]
    # for num in range(0, 2):
    #     thread_list[num].start()
