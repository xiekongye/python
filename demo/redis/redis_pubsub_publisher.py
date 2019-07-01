import redis

if __name__ == '__main__':
    client = redis.StrictRedis()
    client.publish("codehole","xiekongye")
    client.publish("codehole","zhengyizhou")
    client.publish("codehole","xijinping")