import pygame
import requests
from aip import AipOcr
import os
import time
import re

APP_ID = '11444746'
API_KEY = 'UGvLDGzTOmI3HW1QNGLQ85Pv'
SECRET_KEY = 'u7B9qwng8Efi8XDZAl9YIumqVve26NeA'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def get_code():
    r = requests.get('https://www.tianyancha.com/', headers=headers)
    code = re.findall(r'https://static.tianyancha.com/fonts-styles/css/(.*?)/font.css', r.text)[0]
    return code


def change_words(words):
    print('需要转换的字符串：', words)
    code = get_code()
    r = requests.get('https://static.tianyancha.com/fonts-styles/fonts/{}/tyc-num.ttf'.format(code), headers=headers)
    # print(r.content)
    with open('tyc.ttf', 'wb') as f:
        f.write(r.content)
    pygame.init()
    new_words = ''
    for word in words:
        while True:
            try:
                font = pygame.font.Font("tyc.ttf", 64)
                rtext = font.render(word, True, (0, 0, 0), (255, 255, 255))
                filePath = str(words.index(word)) + '.jpg'
                pygame.image.save(rtext, filePath)
                img = get_file_content(filePath)
                client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
                #  调用通用文字识别, 图片参数为本地图片
                result = client.basicAccurate(img)
                # print(result)
                if len(result['words_result']) == 0:
                    new_words += word
                else:
                    for wd in result['words_result']:
                        new_words += wd['words']
                break
            except Exception as E:
                print(E)
                time.sleep(0.5)
                continue
        time.sleep(0.5)
        os.remove(filePath)
    return new_words


if __name__ == '__main__':
    a = change_words('技随办调、技随物找、技随咨询、技随开发、技随夫务；销售自行开发步的年交、文子似交、重似交、红金阳需；软件开发；')
    print('转换后的字符串：', a)

