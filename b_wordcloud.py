import pandas as pd
import numpy as np
from matplotlib.image import imread
import wordcloud
import jieba

# 定义蓝色调色板
def blue_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(210, 100%%, %d%%)" % np.random.randint(50, 90)

# 将数据导入
dm = pd.read_excel('all_dm.xlsx',sheet_name = 'Sheet1')

my_stopwords = ['是', '的', '了', '啊','吗']  # 自定义的停用词列表

# 词云图生成
def wordcloud_generation(dm):
    dm_list = dm['danmu'].tolist() # 弹幕列表
    dm_string = ''.join(dm_list) # 弹幕字符串
    dmreal_string = ' '.join(jieba.lcut(dm_string)) # 分词
    img = imread("yugui.jpg") # 导入图片
    # 词云生成
    wc = wordcloud.WordCloud(
        stopwords=my_stopwords,
        width=1920,
        height=1200,
        background_color='white',
        font_path='msyhl.ttc',
        mask=img,
        max_words=500,
        color_func=blue_color_func,
    ).generate(dmreal_string)
    wc.to_file('danmu_dwordcloud.png')

# 调用词云生成
wordcloud_generation(dm)