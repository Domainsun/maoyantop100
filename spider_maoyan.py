import threading
import requests, re, json
from requests.exceptions import RequestException
from multiprocessing import Process
from multiprocessing import Pool

def get_one_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        with open('result.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            f.close()
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("异常")
        return None


def parse_html(html):
    pattern = re.compile(
        '<dd>.*?>(\d+)</i>.*?data-src="(.*?)".*?"name"><a.*?>(.*?)</a>.*?class="star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',
        re.S)
    items = re.findall(pattern, html)
    # print(items)
    for item in items:
        yield {
            "index": item[0],
            "image": item[1],
            "title": item[2],
            "actor": item[3].strip()[3:],
            "time": item[4].strip()[5:],
            "score": item[5] + item[6]
        }


def write_to_file(content):
    with open('maoyantop100.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

list=[]
def main(offset):
    url = "http://maoyan.com/board/4?offset="+str(offset)
    html = get_one_page(url)

    for item in parse_html(html):
        list.append(item)
        # print(item)
        # write_to_file(item)

if __name__ == '__main__':#git test

    # for循环方式来爬取
    # for i in range(10):
    #     main(i*10)

    #进程方式执行 起了十个进程来爬取，为了保证抓取完成也就是进程执行完毕，加入p.join()方法来保证进程执行完，当前程序才退出，但是这样会使爬取效率降低
    # processes = [Process(target=main,args=(i*10,) ) for i in range(10)]  # 用列表生成式 生成10个线程
    # for p in processes:
    #     p.start()  # 启动刚刚创建的10个进程
    #     p.join()  # 进程结束 主进程也就是当前的程序 才结束
    # print('master process finished...')
    #

    # #进程池 多进程的方式来爬取
    # def end(arg):# 单个进程结束执行的方法
    #     print("processes finish")
    # pool = Pool(5)
    # for i in range(10):
    #     pool.apply(main,args=(i*10,)) #串行执行
    #     # pool.apply_async(func=main, args=(i*10,), callback=end)  # 并行执行，callback，是进程结束后的回调，是主进程调用的回调。
    # pool.close()  # 需先close，再join
    # pool.join()  # join: 等待子进程，主线程再结束
    # print('main finished...')


    #多线程方式爬取 启动十个线程来爬取，爬取速度及其快，可以实现秒获取
    threads=[ threading.Thread(target=main,args=(i*10,)) for i in range(10)] #用列表生成式 生成10个线程
    for t in threads: #启动刚刚创建的10个线程
        t.start()
        t.join() #加入join后 ，子线程结束，主线程才结束，运行速度会变慢
    print(json.dumps(list))
    write_to_file(list)