# coding=utf-8
from hashlib import sha1


def get_hash(str, salt=None):
    '''
    获取一个字符串的hash值
    '''
    str = '!@#$%^&' + str + 'salesmind'
    if salt:
        str = str + salt
    sh = sha1()
    sh.update(str.encode('utf-8'))
    return sh.hexdigest()


if __name__ == '__main__':
    print(get_hash('salesmind'))