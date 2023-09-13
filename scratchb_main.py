import random
import time
import requests
import re
import xml.etree.ElementTree as ET
import pandas as pd
import concurrent.futures
import threading

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}
all_danmus = {}
top20_pending = {}
finish_task_num = 0
lock = threading.Lock()


# 获取b站cookie
def get_cookies():
    return requests.get('https://www.bilibili.com/', headers=headers).cookies.get_dict()


# 将关键词改成utf_8格式
def kw_to_utf_8(keyword):
    keyword = keyword.encode('utf-8')
    keyword = str(keyword)[2:-1].replace('\\x', '%').upper()
    return keyword


# 获取bvid
def get_bvids(keyword, cookies):
    bvids = []
    for page in range(0, 15):
        url = f'https://api.bilibili.com/x/web-interface/wbi/search/type?keyword={keyword}&search_type=video&page={page + 1}'
        bvids.extend(re.findall(r'\"bvid\":\"(\w+)', requests.get(url, headers=headers, cookies=cookies).text))
        print(f'正在获取bvid,进度: {page + 1} / 15')
        time.sleep(round(random.uniform(0, 1), 2))
    return bvids


# 获取cid
def get_cid(bvid):
    cid_url = f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp'
    cid = re.search(r'\"cid\":(\d+)', requests.get(cid_url, headers=headers).text).group(1)
    return cid


# 爬取弹幕
def get_danmu(bvid):
    global all_danmus, top20_pending, finish_task_num
    time.sleep(round(random.uniform(0, 1), 2))
    cid = get_cid(bvid)
    time.sleep(round(random.uniform(0, 1), 2))
    dms = {}
    ans = requests.get(f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}', headers=headers)
    ans.encoding = 'utf-8'
    root = ET.fromstring(ans.text)
    for dm in root.findall('d'):
        if dm.text in dms:
            dms[dm.text] += 1
        else:
            dms[dm.text] = 1
    try:
        lock.acquire()
        for (k, v) in dms.items():
            if k in all_danmus:
                all_danmus[k] += v
            else:
                all_danmus[k] = v
    except:
        print('error:' + bvid)
    finally:
        lock.release()
    if len(dms) > 60:
        dms = sorted(dms.items(), key=lambda x: x[1], reverse=True)[:60]
    else:
        dms = list(dms.items())
    try:
        lock.acquire()
        for (k, v) in dms:
            if k in top20_pending:
                top20_pending[k] += v
            else:
                top20_pending[k] = v
        print(f'当前进度 : {finish_task_num + 1} / 300')
        finish_task_num += 1
    except:
        print('error:' + bvid + 'step2')
    finally:
        lock.release()


def main():
    keyword = kw_to_utf_8(input("请输入你要检索的内容: "))
    cookies = get_cookies()

    bvids = get_bvids(keyword, cookies)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        threads = [executor.submit(get_danmu, bvid) for bvid in bvids]

        concurrent.futures.wait(threads)

    print('爬取完成 ! \n正在生成统计结果。。。')
    top20 = sorted(top20_pending.items(), key=lambda x: x[1], reverse=True)[:20]
    print('统计结果如下:')
    with open('top20.txt', 'w', encoding='utf-8') as f:
        for index, (content, count) in enumerate(top20):
            try:
                f.write(content + ' ' + str(all_danmus[content]) + '\n')
                print("Top{:>3d}:{:<10.10s} , count :{:>5d}".format(index + 1,
                                                                      content[:7] + '...' if len(content) > 7 else content,
                                                                      all_danmus[content]))
            except:
                pass
    print('由于控制台输出长度受限,部分弹幕可能显示不全，请移步项目根目录下top.txt文件中查看详情')

    df = pd.DataFrame([{'danmu': k, 'count': v} for k, v in all_danmus.items()])
    df.to_excel('all_dm.xlsx', index=False)
    print('Excel表格导入完成')


if __name__ == '__main__':
    main()
