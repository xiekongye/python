import random
import os
import json


if __name__ == '__main__':
    for i in range(10):
        print(random.randint(1, 10))

    names = ['xiekongye', 'xijinping', 'anqila']
    for i in range(10):
        print(random.choice(names))

    print(os.getcwd())
    print(os.listdir('F:\\'))
