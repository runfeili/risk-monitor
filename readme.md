# Risk Monitor

> 基于 Bloomberg、Google News 和 Gemini 的贷后风险监控系统。


## 系统流程
<img src="assets/pipeline.svg" width="900">


## 项目结构

```text
risk-monitor/
│
├── input/             # 输入文件
├── output/            # 输出结果
├── logs/              # 日志
│
├── src/
│   ├── main.py        # 主程序入口
│   ├── configs.py     # 配置文件
│   ├── context.py     # 数据结构设计
│   │
│   ├── metrics/       # Bloomberg 指标计算
│   ├── spiders/       # Google News 新闻爬取
│   ├── llm/           # 大模型相关模块
│   │ 
│   └── utils/         # 工具函数
│
├── requirements.txt
└── README.md
```

## 配置与运行

### 环境要求
- Python >= 3.11
- Bloomberg Terminal
- Gemini API Key

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

项目使用 `.env` 管理 Gemini API Keys。

示例：

```env
GEMINI_API_KEYS=key1,key2,key3
```

支持多个 Key 自动轮换。

### 修改运行参数

主要配置位于：

```text
src/configs.py
```

### 使用方法
输入企业名单：

```text
input/company_list.xlsx
```

运行主程序：

```bash
python src/main.py
```



程序运行结束后将在`outout/`生成结果。

运行日志位于：

```text
logs/
```
