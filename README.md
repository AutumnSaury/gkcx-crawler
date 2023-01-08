# 一个掌上高考爬虫

一个用来从[掌上高考](https://www.gaokao.cn/)爬取高校分数线的爬虫。

## 使用指北

要运行这个爬虫，您需要：
- 一个Python运行时，推荐使用3.10或以上版本
- 一台可以长期运行的计算机设备
- 一些耐心

### 安装依赖

首先，您需要使用pip安装requirements.txt中的依赖。

```bash
$ pip install -r requirements.txt
```

### 配置

您需要参照注释修改`main.py`顶部的几个常量以适应您的需求。

### 运行

最后，运行爬虫即可

```bash
$ python main.py
```

根据您的配置，完全爬取数据需要的时间可能在几小时到几天不等，请耐心等待。  
被爬取的数据将保存在脚本同目录下的`csv`文件中。