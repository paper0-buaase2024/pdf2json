## Description

- 任务
    - 批量下载 arxiv pdf
    - pdf数据转换到Json
    - 注意 长度，格式
- input & output
    - 批量下载指定 id 的 pdf
    - pdf 解析成文本
    - 文本截掉引用和原本摘要（统计长度，及时反馈）
    - 将文本转换到要求的json格式（如下，只需要填prompt(填入全文)和id(填入提供的指定id的字符串)）
- 结果
    - 一套根据文章信息json批量下载pdf的工具
    - 将 pdf 解析成文本并筛除摘要内容的工具
    - 流畅运行以上流程，导出到要求的json字符串
  

INPUT: arxiv_papers.json
``` json
[
    {
        ...,
	    "id": "",
        ...
    },...
]

```

OUTPUT: result.json
``` json
[
    {
	    "history": "",
	    "prompt": "",
	    "response": "",
	    "task_level_1": "",
        "len": "",
	    "id": ""
    },...
]
```