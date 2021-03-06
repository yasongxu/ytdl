# ytdl

ytdl：将youtube的视频转化为一篇文章，比如一键将pycon2018的所有视频演讲变成系列文章。

### 背景

在youtube上做新技术调研的时候看到了一篇峰会的演讲，视频很长，但又想快速了解演讲的内容，于是想到直接下载字幕，但有些小的问题：

1. 有些视频没有字幕，尤其是一些技术大会视频（当然你可以点击youtube的自动生成英文字幕）
2. 字幕文件可以下载，却是时间轨+台词的格式，无法拿来直接阅读，如srt文件
3. 从字幕中拿出了所有台词，发现只有一句，因为没有标点符号，也不知道该怎么断句。


于是做了些微小的工作：

1. 使用youtube的python sdk下载视频的字幕文件(vtt格式)，没有字幕的视频youtube也能做语音识别返回字幕文件，语言：英文
2. 将字幕文件中的文字部分提取出来，合并为一段文字
3. 开始断句：基于时间轨中的台词停留时间 + 语义分析([punctuator analysis](http://bark.phon.ioc.ee/punctuator))
4. 得到一篇有标点、分段的文章，并配图转换为html文件
5. 支持youtube中的channel，处理一组视频文件



### 示例

运行：python ytdl.py --help

使用pyinstaller进行程序的打包，也可以在release中下载二进制运行


```
单视频：./ytdl --video_id=AjFfsOA7AQI

视频集：./ytdl --channel_id=UCrJhliKNQ8g0qoE_zvL8eVg

```

可以在当前目录得到如下文件：


```
html：可直接打开的html文件
txt：txt版文件
punctuate：分词后的文件
sub：原始字幕文件
```

### 注意事项

* 1. 对于没有字幕的视频，字幕来源是youtube自带的在线自动生成字幕，即语音分析。因此由于演讲人的发音问题，得到的文字也可能是不准确的，最终产出的文章内容如果比较奇怪，要有心理准备~

* 2. 由于pyinstaller无法跨平台编译，目前的release中只有linux和mac版，有需要的可以自行编译

```
pyinstaller -F --hidden-import apiclient  ytdl.py
```

* 3. youtube是在qiang外，脚本所在环境需要能通外网。



![](https://vermouth2018.oss-cn-qingdao.aliyuncs.com/product/15612825612411.jpg?x-oss-process=style/xxx)


