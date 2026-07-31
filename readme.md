# Risk-Monitor 编程手册

本系统利用 **Bloomberg** 获取财务和新闻情绪指标，结合 **Google News** 检索公开新闻，借助 **Gemini** 进行风险识别与补充搜索，最终自动生成企业负面新闻监测报告。

## 1 项目概述

系统主要由四个核心模块构成：

1. **指标计算**：调用 Bloomberg API，提取财务指标、新闻情绪指标，并加权生成综合风险评分。
2. **新闻爬取**：调用 Google News 封装库 gnews 进行新闻爬取。
3. **新闻风险判断**：调用 Gemini API，对爬取的新闻进行风险判断与分类分析。
4. **新闻补充搜索**：调用 Gemini API 并使用 Google Search Tool，对负面风险新闻进行补充搜索。

系统流程图：
<img src="assets/pipeline.svg" width="800">

## 2 目录结构

```text
risk-monitor/
├── input/             					 # 输入文件
│   ├── company_list.xlsx        # 企业客户列表
│   ├──         					 			 # 
├── output/            					 # 输出结果
├── logs/              					 # 日志
├── src/
│   ├── main.py        					 # 主程序入口
│   ├── test.py 								 # 只进行新闻搜索的测试程序
│   ├── config.py      					 # 配置参数
│   ├── context.py     					 # 运行中的上下文数据结构
│   ├── metrics/       		 			 # Bloomberg 指标计算
│   │ 	├── bbg_client.py      	 # 连接和调用 Bloomberg API
│   │   ├── financial_metrics.py # 获取财务指标
│   │   ├── news_metrics.py   	 # 获取新闻情绪指标
│   │   └── risk_score.py     	 # 计算综合风险评分
│   ├── spiders/       					 # Google News 新闻爬取
│   │   └── news_spider.py       # 连接和调用 gnews 库获取新闻 
│   ├── llm/           					 # 大语言模型相关模块
│   │   ├── api_key.py         	 # Gemini API Key 管理与轮询机制
│   │   ├── gemini.py            # 连接和调用 Gemini API
│   │   ├── llm_agent.py         # 使用 LLM 生成和解析文本
│   │   ├── news_classifier.py   # 新闻风险判断与分类
│   │   ├── news_searcher.py   	 # 负面风险新闻补充搜索
│   │   ├── prompts.py           # Prompt 加载
│   │   └── prompts/             # Prompt 模板文本内容
│   │       ├── news_classifier_v1.txt
│   │       └── news_searcher_v1.txt
│   └── utils/         					 # 通用工具函数
│			  ├── date_utils.py        # 日期处理与格式化
│       ├── excel_utils.py       # Excel 生成与格式设计
│       ├── logger.py            # 日志生成
│       ├── path_utils.py        # 路径生成与管理
│       └── pipeline_utils.py    # 上下文数据结构生成
├── .env
├── requirements.txt
└── README.md
```

## 3 环境准备

- 环境要求

  - Python >= 3.11
- Bloomberg Terminal


- 安装依赖

  ```bash 
  pip install -r requirements.txt
  ```

## 4 运行方法

1. 连接互联网并登录Bloomberg Terminal。
2. 在 `input/company_list.xlsx` 输入企业客户名单。
3. 在 `src/config.py` 修改相关参数。
4. 在 `.env` 配置 Gemini API Keys。
5. 运行主程序 `src/main.py`。
6. 等待程序运行结束，生成结果保存在 `output/`，运行日志保存在 `logs/`。

## 5 程序

