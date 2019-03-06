import os, re, sys
import urllib.request, urllib.error, requests
from multiprocessing import Pool


# 打开并读取网页内容
def getUrlData(url):
    try:
        return urllib.request.urlopen(url, timeout=200)
    except Exception as err:
        print(f'err getUrlData({url})\n', err)
        return -1


def getM3u8url(api, videoUrl):
    print("使用的解析接口为：" + api)
    print("官网地址是:" + videoUrl)
    res = requests.get(api + videoUrl)
    title = re.findall(r"<title>(.+?)</title>", res.text)[0]
    url_m3u8 = re.findall(r'url=(.+?)"', res.text)[0]
    return title, url_m3u8


def getTsList(url):
    host = url[:url.index("/", 8)]
    print(url)
    resData = getUrlData(url)
    num = 0
    lsList = list()
    for line in resData:
        lineText = line.decode('utf-8').replace("\n", "")
        if lineText.endswith(".m3u8"):
            return getTsList(host + lineText)
        if lineText.endswith(".ts"):
            if lineText.startswith("http"):
                lsList.append(lineText)
            else:
                if lineText.startswith("/"):
                    lsList.append(host + lineText)
                else:
                    lsList.append(url[:url.rfind('/')] + "/" + lineText)
            num = num + 1
    return set(lsList)


def down_ts_file(a):
    url = a[0]
    path = a[1]
    print("正在下载..." + url)
    filename = path + url[url.rfind('/'):]
    urllib.request.urlretrieve(url, filename)


def buildMp4(path, title):
    path = os.path.abspath(path)
    cmd = r"copy /b " + path + "\*.ts " + path + "\\" + title + ".mp4"
    print(cmd)
    os.system(cmd)
    print("视频合并成功")
    del_cmd = f'del {path}\*.ts'
    print(del_cmd)
    os.system(del_cmd)


if __name__ == '__main__':

    api = "https://jx.618g.com/?url="
    if (len(sys.argv)) <= 1:
        video_url = input("请输入官网视频的地址")
    else:
        video_url = sys.argv[1]
    print(video_url)
    title, m3u8Url = getM3u8url(api, video_url)
    lsVideoSet = getTsList(m3u8Url)
    print("你要下载的视频是：" + title)
    print("视频总数为:%d" % len(lsVideoSet))
    path = "./" + title
    if not os.path.exists(path):
        os.makedirs(path)
    pool = Pool(200)
    pool.map(down_ts_file, [(ts, path) for ts in lsVideoSet])
    buildMp4(path, title)
