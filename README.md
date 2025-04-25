# D5_Exam

## ML
先通过\n字符将数据文本分割，提取每一个问题，再通过正则表达式将后面的Yes\No提取，组合成一个具体的问题。再通过MD5算法生成hash ID。
对于额外的tag，查看原论文发现该Headline数据来自于一篇论文Impact of News on the Commodity Market: Dataset and Results，该论文中对每个Headline都打了标签，因此可以根据该论文的数据对问题打上不同的tag。

## 爬虫
借助Cursor，编写一个爬虫脚本，在每个翻页请求前设置1秒延迟
输出格式
- title: 工作名称
- location: 工作地点 
- posted_date: 发布日期
- job_id: 工作ID
- url: 工作详细信息网址