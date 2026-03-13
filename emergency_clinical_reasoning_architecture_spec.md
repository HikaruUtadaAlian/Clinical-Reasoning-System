# 急诊病例推理系统架构文档（供 Codex 执行）

## 1. 文档目的

本文档定义一个面向急诊场景的**可解释病例推理系统**的技术架构、最小可行 Demo 方案、未来产品最终形态，以及 Codex 的执行边界。目标是让 Codex 能直接按文档搭建第一版工程，同时保证后续能自然扩展到知识图谱、GraphRAG、多智能体协作和在线部署。

---

## 2. 产品定义

### 2.1 产品名称（工作名）

**Emergency Clinical Reasoning System**

中文可用名：**急诊病例智能推理系统**

### 2.2 核心定位

输入一段病例描述，系统输出：

1. Top-K 鉴别诊断
2. 每个诊断的支持证据
3. 推荐检查
4. 初步处理建议
5. 引用来源
6. 推理过程摘要

### 2.3 目标用户

- 导师 / 评审：看系统架构、可行性、创新性
- 学生开发者：快速验证医学 AI 工作流
- 后续可扩展用户：医学生、科研团队、临床教学场景

### 2.4 MVP 演示目标

第一版 Demo 只要求完成：

- 支持一个症候群：**胸痛**
- 支持三个疾病：
  - STEMI
  - 主动脉夹层
  - 肺栓塞
- 支持输入一段中文病例文本
- 支持结构化输出结果
- 必须包含 **LangGraph 多节点工作流**
- 必须包含 **文档检索 + 图谱检索**
- 必须能展示引用证据

---

## 3. 范围定义

### 3.1 Demo 必做

- 本地 JSON 数据集
- 本地知识图谱 JSON
- LangGraph 工作流
- Streamlit 前端
- 结构化输出
- 至少 2 个演示病例

### 3.2 Demo 不做

- 全量 180 PDF 自动解析
- 复杂数据库
- 复杂权限系统
- 真正的医院决策支持合规系统
- 生产级 Neo4j 集群
- 多轮人机协商
- 医疗责任声明之外的临床落地

---

## 4. 系统总体架构

系统采用五层结构：

1. **数据层**：病例样例、文档 chunk、知识图谱
2. **检索层**：文档检索器、图谱检索器
3. **推理层**：LangGraph 编排的多节点流程
4. **展示层**：Streamlit 页面
5. **扩展层**：未来用于 PDF 解析、GraphRAG 增强、部署与监控

### 4.1 数据流

病例输入
→ 病例解析
→ 文档检索 / 图谱检索（并行）
→ 推理整合
→ 结构化输出
→ 页面展示

---

## 5. 多智能体 / LangGraph 架构

第一版不做“自由对话型多智能体”，而是做**职责明确的工作流型多智能体**。

### 5.1 节点定义

#### Agent 1: Case Parser
职责：
- 从病例文本中抽取结构化要素
- 识别年龄、性别、主诉、症状、体征、检查结果
- 生成用于检索的关键词列表

输入：
- case_text

输出：
- parsed_case
- query_terms

#### Agent 2: Document Retriever
职责：
- 在文档 chunks 中检索与病例最相关的证据片段
- 返回若干带来源的 chunk

输入：
- query_terms
- parsed_case

输出：
- doc_hits

#### Agent 3: Graph Retriever
职责：
- 在知识图谱中查找与症状 / 检查结果匹配的疾病与邻居节点
- 返回候选疾病、相关症状、检查、治疗节点

输入：
- query_terms
- parsed_case

输出：
- graph_hits
- candidate_diseases

#### Agent 4: Reasoner
职责：
- 综合文档证据和图谱证据
- 输出 Top-K 鉴别诊断
- 生成支持证据、建议检查、初步处理、引用来源

输入：
- parsed_case
- doc_hits
- graph_hits
- candidate_diseases

输出：
- final_answer

### 5.2 图结构

```text
START
  ↓
case_parser
  ↓
[doc_retriever || graph_retriever]
  ↓
reasoner
  ↓
END
```

### 5.3 为什么这样设计

- Demo 需要“多智能体”但必须可控
- LangGraph 适合状态驱动、节点明确的工作流
- 这样既能展示 agent 化，又不把系统做成混乱的大杂烩

---

## 6. 状态设计（LangGraph State）

使用共享状态对象，建议如下：

```python
from typing import TypedDict, List, Dict, Any

class AppState(TypedDict, total=False):
    case_text: str
    parsed_case: Dict[str, Any]
    query_terms: List[str]
    doc_hits: List[Dict[str, Any]]
    graph_hits: List[Dict[str, Any]]
    candidate_diseases: List[Dict[str, Any]]
    final_answer: Dict[str, Any]
    logs: List[str]
```

### 6.1 字段说明

- `case_text`: 原始病例文本
- `parsed_case`: 抽取后的结构化病例
- `query_terms`: 用于检索的关键词
- `doc_hits`: 文档检索返回的证据片段
- `graph_hits`: 图谱检索返回的节点和边信息
- `candidate_diseases`: 图谱检索推导出的候选疾病
- `final_answer`: 最终输出 JSON
- `logs`: 调试日志

---

## 7. 数据设计

### 7.1 文档数据：chunks.jsonl

每行一个医学证据片段。

示例：

```json
{"id":"c1","disease":"STEMI","text":"STEMI常表现为持续性胸痛、出汗，ECG可见ST段抬高，需尽快启动再灌注治疗。","source":"doc1.pdf#p12"}
```

字段：
- `id`: chunk 唯一标识
- `disease`: 主要相关疾病
- `text`: 证据文本
- `source`: 来源标识

### 7.2 图谱数据：graph.json

```json
{
  "nodes": [
    {"id":"STEMI","type":"disease"},
    {"id":"胸痛","type":"symptom"},
    {"id":"出汗","type":"symptom"},
    {"id":"ST段抬高","type":"finding"},
    {"id":"Troponin","type":"test"}
  ],
  "edges": [
    {"source":"STEMI","target":"胸痛","type":"has_symptom"},
    {"source":"STEMI","target":"出汗","type":"has_symptom"},
    {"source":"STEMI","target":"ST段抬高","type":"has_finding"},
    {"source":"STEMI","target":"Troponin","type":"requires_test"}
  ]
}
```

### 7.3 推荐实体类型

第一版：
- disease
- symptom
- sign
- finding
- test
- treatment
- drug
- complication

### 7.4 推荐关系类型

第一版：
- has_symptom
- has_sign
- has_finding
- requires_test
- treated_by
- may_cause

---

## 8. 检索设计

### 8.1 文档检索

第一版优先实现简单方案：
- 关键词匹配 / BM25 / 简单 embedding 检索

要求：
- 返回 top_k 个相关 chunk
- 每条结果必须带 `source`

### 8.2 图谱检索

输入病例关键词后：
- 找到匹配的 symptom/finding 节点
- 沿边找到相关 disease
- 收集 disease 的邻居信息

输出示例：

```json
[
  {
    "disease": "STEMI",
    "matched_nodes": ["胸痛", "出汗", "ST段抬高"],
    "tests": ["Troponin", "ECG"],
    "treatments": ["Aspirin", "PCI"]
  }
]
```

### 8.3 混合策略

最终 Reasoner 同时接收：
- 文本证据：来自文档
- 关系证据：来自图谱

这就是第一版的“轻量 GraphRAG”。

---

## 9. 推理输出设计

输出必须固定为结构化 JSON，禁止仅返回长段自然语言。

建议格式：

```json
{
  "case_summary": "65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。",
  "candidate_diagnoses": [
    {
      "name": "STEMI",
      "rank": 1,
      "confidence": 0.86,
      "supporting_evidence": ["胸痛", "出汗", "ST段抬高"],
      "against_evidence": [],
      "recommended_tests": ["Troponin"],
      "initial_management": ["Aspirin", "PCI pathway"],
      "citations": ["doc1.pdf#p12"]
    }
  ],
  "next_steps": ["完善肌钙蛋白检测", "持续监测生命体征"],
  "notes": "该结果用于教学与演示，不构成临床建议。"
}
```

---

## 10. 前端展示设计

前端使用 Streamlit，页面包括：

1. 标题区
2. 病例输入框
3. 分析按钮
4. 结果区：
   - 病例摘要
   - Top-3 诊断
   - 支持证据
   - 建议检查
   - 初步处理
   - 引文来源
5. 调试区：
   - 文档命中结果
   - 图谱命中结果
   - LangGraph 节点执行日志

### 10.1 演示友好原则

- 页面必须一眼能看懂
- 输出不要像聊天记录
- 尽量像“病例分析报告”

---

## 11. 项目目录结构

```text
emergency-demo/
├── app/
│   ├── streamlit_app.py
│   └── components.py
├── data/
│   ├── chunks.jsonl
│   ├── graph.json
│   └── demo_cases.json
├── src/
│   ├── state.py
│   ├── graph_workflow.py
│   ├── agents/
│   │   ├── case_parser.py
│   │   ├── doc_retriever.py
│   │   ├── graph_retriever.py
│   │   └── reasoner.py
│   ├── retrieval/
│   │   ├── text_search.py
│   │   └── graph_search.py
│   ├── utils/
│   │   ├── io.py
│   │   ├── logger.py
│   │   └── formatting.py
│   └── prompts/
│       └── reasoner_prompt.txt
├── tests/
│   ├── test_case_parser.py
│   ├── test_retrieval.py
│   └── test_workflow.py
├── requirements.txt
├── README.md
└── AGENTS.md
```

---

## 12. Codex 执行指令

### 12.1 Codex 的目标

Codex 应按以下顺序完成项目：

1. 创建项目目录与基础文件
2. 写入示例数据
3. 实现状态定义
4. 实现 4 个 agent 节点
5. 用 LangGraph 串联工作流
6. 实现 Streamlit 页面
7. 写 README 与运行说明
8. 运行并修复阻塞错误

### 12.2 Codex 不应做的事

- 不要擅自引入复杂数据库
- 不要擅自改成微服务
- 不要擅自加入额外 agent
- 不要擅自把项目改成训练型模型
- 不要引入超重依赖，除非必要

### 12.3 Codex 代码风格要求

- 代码应模块化
- 每个模块职责单一
- 函数应有清晰注释
- 尽量使用简单实现
- 优先保证可运行，再优化优雅性

### 12.4 AGENTS.md 要求

仓库中必须包含 `AGENTS.md`，写明：

- 项目目标
- 不要扩大范围
- 当前只做胸痛三病种 Demo
- 优先本地 JSON 数据
- 优先工作流稳定而非功能膨胀
- 修改后必须运行基本自检

---

## 13. Demo 验收标准

以下全部满足才算第一版完成：

1. 输入一段胸痛病例文本后，系统可返回结果
2. 系统内部使用 LangGraph 工作流
3. 至少存在 4 个明确节点
4. 输出包含 Top-3 候选诊断
5. 输出包含支持证据
6. 输出包含推荐检查
7. 输出包含初步处理
8. 输出包含来源引用
9. 页面能展示文档命中与图谱命中
10. 至少准备 2 个演示病例

---

## 14. 推荐演示病例

### 病例 A

65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。

预期重点：
- STEMI 排名靠前

### 病例 B

58岁男性，突发胸背部撕裂样疼痛，双上肢血压不一致。

预期重点：
- 主动脉夹层排名靠前

### 病例 C

42岁女性，突发胸痛伴呼吸困难，心动过速，D-dimer升高。

预期重点：
- 肺栓塞排名靠前

---

## 15. 未来产品最终形态规划

第一版 Demo 只是最小闭环。最终产品形态应演进为一个**面向急诊与教学场景的可解释临床推理平台**。

### 15.1 最终产品愿景

构建一个支持：
- 病例推理
- 疾病问答
- 证据检索
- 医学知识图谱浏览
- 推理过程可解释
- 报告导出
- 多病种扩展
- 多模态输入

的综合平台。

### 15.2 最终产品模块

#### A. 文档处理中心
- 批量导入 PDF
- OCR / 文本抽取
- 自动切块
- 元数据管理
- 引文定位

#### B. 医学知识图谱中心
- 实体抽取
- 关系抽取
- 图谱版本管理
- 图谱浏览器
- 图谱质量评估

#### C. GraphRAG 引擎
- 文本向量检索
- 图谱路径检索
- 混合检索重排序
- 来源归因

#### D. 病例推理引擎
- 鉴别诊断
- 检查推荐
- 初步处理建议
- 风险提示
- 推理轨迹生成

#### E. 多智能体协作层
未来可扩展出：
- Case Parser Agent
- Evidence Retrieval Agent
- Guideline Agent
- Differential Diagnosis Agent
- Safety Checker Agent
- Report Generator Agent
- Judge / Synthesizer Agent

#### F. 报告与展示层
- Web UI
- 结构化病例报告
- PDF 导出
- 教学模式 / 演示模式
- API 接口

---

## 16. 未来演进路线图

### Phase 1：Demo 原型
- 胸痛三病种
- 本地 JSON 数据
- LangGraph 基础工作流
- Streamlit 演示

### Phase 2：小规模真实知识库
- 接入部分真实 PDF
- 自动 chunk
- embedding 检索
- 更规范的引用链

### Phase 3：知识图谱增强
- 自动实体关系抽取
- 引入 Neo4j 或图数据库
- 路径级证据解释

### Phase 4：临床推理增强
- 引入更多病种
- 多症候群支持
- 更丰富的规则 / 指南整合
- 安全校验层

### Phase 5：产品化
- 用户系统
- 案例库管理
- 报告导出
- 在线部署
- 教学平台集成

---

## 17. 技术栈建议

### 第一版 Demo
- Python
- LangGraph
- Streamlit
- JSON / JSONL
- 可选：networkx
- 可选：简单关键词检索 / BM25 / 轻量 embedding

### 后续扩展
- FastAPI
- PostgreSQL
- Neo4j
- FAISS / Chroma / Qdrant
- Docker
- Nginx
- 云服务器部署

---

## 18. 风险与约束

### 18.1 当前最大风险

- 范围膨胀
- 为了“高级”而过度设计
- 把 demo 做成难以调试的多智能体迷宫
- 输入输出格式不稳定

### 18.2 控制策略

- 先固定三病种
- 先手工构造小数据集
- 先工作流后智能化
- 先可跑通后再扩展

---

## 19. 交付物清单

第一版应交付：

1. 源代码仓库
2. 可运行的 Streamlit 页面
3. 示例数据文件
4. README 运行说明
5. AGENTS.md
6. 两到三个演示病例
7. 一页简短项目说明（给导师演示时使用）

---

## 20. 给 Codex 的最终执行口令

可直接将以下内容作为 Codex 顶层任务输入：

```text
Build a minimal but clean demo for an emergency clinical reasoning system.

Constraints:
- Use Python
- Use LangGraph for orchestration
- Use Streamlit for UI
- Use local JSON/JSONL files as demo data
- Support one syndrome: chest pain
- Support three diseases: STEMI, aortic dissection, pulmonary embolism
- Implement 4 workflow agents: case_parser, doc_retriever, graph_retriever, reasoner
- Output structured JSON with diagnoses, supporting evidence, recommended tests, initial management, and citations
- Keep the code simple, modular, and runnable locally
- Add README and AGENTS.md
- Do not overengineer
```

---

## 21. 一句话总结

**第一版不是做“完整医学 AI 平台”，而是做一个能让导师看见架构方向、能实际跑起来、能展示 LangGraph 多智能体与轻量 GraphRAG 思路的临床推理 Demo。**

