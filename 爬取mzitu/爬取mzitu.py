import requests
from bs4 import BeautifulSoup
import os
import threading
import time

header = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'https://www.mzitu.com/'
}
path = 'D:/mzitu/'


def download_page(url):
    r = requests.get(url, headers=header)
    return r.text


def get_pic_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    pic_list = soup.find('ul', id="pins").find_all('a')
    for a in pic_list:
        title = a.text
        if title != '':
            print('准备爬取:' + title)
            max_pic = get_max_pic(a['href'])
            if create_dir(title, max_pic):
                get_pic(a['href'], max_pic, title)


def get_pic(url, max_pic, title):
    for num in range(1, int(max_pic) + 1):
        pic_url = url + '/' + str(num)

        r = requests.get(pic_url, headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        img_url = soup.find('img', alt=title)
        print(img_url['src'])

        r = requests.get(img_url['src'], headers=header)
        filename = img_url['src'].split('/')[-1]

        with open(path + title + '/' + filename, 'wb') as f:
            f.write(r.content)
        time.sleep(3)


def get_max_pic(url):
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, "html.parser")
    pic_max = soup.find_all('span')[9].text
    return pic_max


def create_dir(title, max_pic):

    if os.path.exists(path + title):
        flag = 1
    else:
        os.makedirs(path + title)
        flag = 0
    os.chdir(path + title)
    if flag == 1 and len(os.listdir(path + title)) >= int(max_pic):
        print('保存完毕')
        return False
    else:
        return True


def execute(url):
    get_pic_list(download_page(url))


def main():
    max_page = 29
    queue_page = [i for i in range(1, max_page + 1)]
    threads = []
    while len(queue_page) > 0:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < 5:
            cur_page = queue_page.pop(0)
            url = 'https://www.mzitu.com/japan/page/{}'.format(cur_page)
            thread = threading.Thread(target=execute, args=(url, ))
            thread.setDaemon(True)
            thread.setName('Thead - {}'.format(cur_page % 5))
            thread.start()
            print('{}正在下载{}页'.format(thread.name, cur_page))
            threads.append(thread)


if __name__ == '__main__':
    main()
