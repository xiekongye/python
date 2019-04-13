import os


class FileUtils:
    def __init__(self):
        pass

    @staticmethod
    def file_oper_demo(file_path):
        f = open(file_path, encoding='UTF-8')
        users = f.readlines()
        for user in users:
            print(user.strip())
        f.close()

    @staticmethod
    def file_write_demo(file_path, content):
        f = open(file_path, mode='a', encoding='UTF-8')
        f.write(content)
        f.close()

    @staticmethod
    def file_stat_demo(file_path):
        return os.stat(file_path).st_size


if __name__ == '__main__':
    FileUtils.file_oper_demo('user.txt')
    FileUtils.file_write_demo('user_write.txt', '写入一串内容')
    print('File stat : ' + str(FileUtils.file_stat_demo('user_write.txt')))


