# 一个掌上高考爬虫

一个用来从[掌上高考](https://www.gaokao.cn/)爬取高校分数线的爬虫。

## 使用指北

要使用此爬虫，您需要：
- 一个Python运行时，推荐使用3.10或以上版本，最低的可运行此程序的版本为3.9
- 一台可以长期（24小时以上）连续运行的计算机设备
- 稳定的网络环境
- 一些耐心

### 安装依赖

首先，您需要使用pip安装requirements.txt中的依赖。

```bash
$ pip install -r requirements.txt
```

### 配置

您需要参照注释修改定义在`main.py`顶部的几个常量以适应您的需求。

### 运行

最后，运行爬虫即可

```bash
$ python main.py
```

根据您的配置，完全爬取数据需要的时间可能在几小时到几天不等，请耐心等待。  
被爬取的数据将保存在脚本同目录下的`csv`（和可选的`xlsx`）文件中。

> 作为参考，`QUERY_INTERVAL`设置为10时，爬取郑州大学的专业分数线约需要20分钟，招生计划约需要30分钟，各省分数线仅需约3分钟，可作为最坏情况进行估计。

## 附带工具

### merge.py

可用于合并表格，以下是帮助信息：

```bash
$ python merge.py --help
Usage: merge.py [OPTIONS]

  合并多个CSV或XLSX文件，也可用于转换表格格式

Options:
  -c, --csv PATH                  CSV文件路径，此选项可重复使用
  -x, --xlsx PATH                 XLSX文件路径，此选项可重复使用
  -t, --type [csv|xlsx]           输出文件类型，默认为csv，输出的文件将位于当前工作目录下
  --remove-empty-lines / --no-remove-empty-lines
                                  是否使生成文件中不包含来自CSV源文件的空行，默认开启
  --help                          展示帮助信息
```

#### 示例

将两个csv表格合并，导出xlsx格式文件：
```bash
python manage.py -c 1.csv -c 2.csv -t xlsx
```

将两个xlsx表格合并，导出csv格式文件：
```bash
python manage.py -x 1.xlsx -x 2.xlsx -t csv
```