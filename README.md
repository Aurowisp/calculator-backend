# Calculator Backend

## 项目介绍

这是前后端分离计算器系统的 Backend，使用分层结构组织代码。

当前为 Phase 5 - SQLite Database + Calculation History。后端提供安全的数学表达式计算，并使用 SQLite 持久化成功计算的历史记录。

## 技术栈

- Python 3.x
- FastAPI
- Uvicorn
- SQLite
- SQLAlchemy

## 项目结构

```text
calculator-backend/
├── src/
│   ├── main.py                    # FastAPI 入口、中间件和 Router 注册
│   ├── controller/                # HTTP API 路由层
│   │   ├── calculator_controller.py
│   │   └── history_controller.py
│   ├── service/                   # 业务用例协调层
│   │   ├── calculator_service.py
│   │   └── history_service.py
│   ├── calculator/                # 安全的表达式解析与执行模块
│   │   ├── exceptions.py
│   │   ├── parser.py
│   │   └── evaluator.py
│   ├── model/                     # ORM 模型与 Pydantic API 模型
│   │   ├── calculation.py
│   │   ├── history.py
│   │   └── history_schema.py
│   └── database/                  # SQLAlchemy 配置与 Session 管理
│       └── database.py
├── requirements.txt
├── README.md
├── codestyle.md
├── tests/
│   ├── conftest.py
│   ├── test_calculate_api.py
│   ├── test_calculator.py
│   └── test_history_api.py
└── .gitignore
```

各 Python 子目录均包含 `__init__.py`，以便作为独立包导入。

### 分层职责

- `controller`：接收 HTTP 请求并定义 API 路由。
- `service`：编排计算与历史记录业务，避免业务逻辑进入 Controller。
- `calculator`：负责安全的表达式解析和计算执行，不依赖 FastAPI。
- `model`：定义 SQLAlchemy ORM 模型和 Pydantic API 模型。
- `database`：配置 SQLAlchemy Engine，并管理数据库 Session。

## 环境配置

需要安装 Python 3.x。推荐在项目根目录创建独立虚拟环境：

```bash
python -m venv venv
```

Windows 激活命令：

```powershell
venv\Scripts\activate
```

## 安装

激活虚拟环境后安装最小依赖：

```bash
pip install -r requirements.txt
```

## 启动

在 `calculator-backend` 项目根目录运行：

```bash
uvicorn src.main:app --reload
```

服务默认运行在 `http://localhost:8000`。开发环境 CORS 当前允许来自 `http://localhost:5500` 的前端请求。

首次启动时会自动创建数据库及所需数据表。

## API

当前接口：

```http
GET /
```

预期响应：

```json
{
  "message": "Calculator Backend Running"
}
```

可通过浏览器访问：

- 服务状态：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`

### 计算接口

```http
POST /api/calculate
Content-Type: application/json
```

请求：

```json
{
  "expression": "1+2"
}
```

成功响应：

```json
{
  "success": true,
  "expression": "1+2",
  "result": 3
}
```

每次成功计算都会写入数据库；非法表达式、空表达式和除零不会生成历史记录。

无效表达式返回 `400 Bad Request`：

```json
{
  "success": false,
  "message": "Invalid expression"
}
```

缺失字段或字段类型错误由 FastAPI/Pydantic 返回 `422 Unprocessable Entity`。

### 获取历史记录

```http
GET /api/history
```

返回按 ID 从大到小排列的记录，最新记录在前。没有记录时返回 `200 OK` 和空数组：

```json
[]
```

包含记录时返回：

```json
[
  {
    "id": 3,
    "expression": "(1+2)*3",
    "result": 9,
    "created_at": "2026-10-01T10:22:00"
  }
]
```

### 删除历史记录

```http
DELETE /api/history/{id}
```

成功响应：

```json
{
  "success": true,
  "message": "History record deleted"
}
```

记录不存在时返回 `404 Not Found`：

```json
{
  "success": false,
  "message": "History record not found"
}
```

### HTTP 状态码

- `200`：计算、查询或删除成功。
- `400`：数学表达式无效或除零。
- `404`：要删除的历史记录不存在。
- `422`：请求体或路径参数未通过 FastAPI/Pydantic 校验。
- `500`：数据库等内部操作失败；响应不会暴露 SQL 或服务器路径。

核心计算全部由后端完成。解析器不会使用 `eval()`、`exec()`、`compile()`，也不会把用户表达式作为 Python 程序执行。

## Expression Parsing

项目使用手写 Recursive Descent Parser（递归下降解析器）。Tokenizer 首先将输入转换为数字、运算符、括号和结束标记；Parser 再按以下语法层级生成受控语法树：

```text
expression → term (("+" | "-") term)*
term       → unary (("*" | "/") unary)*
unary      → ("+" | "-") unary | primary
primary    → NUMBER | "(" expression ")"
```

- `expression` 处理低优先级的加减法。
- `term` 处理高优先级的乘除法。
- `unary` 区分一元正负号与二元加减法。
- `primary` 处理整数、小数和嵌套括号。

Parser 必须消费全部 Token，因此 `1 2`、`2(3+4)` 或尾随非法内容不会被部分计算。当前支持：

- 四则运算和从左到右结合
- 运算符优先级
- 嵌套括号
- 整数与小数，包括 `.5`
- 一元正号和一元负号
- 空格和 Tab
- 非法字符及非法语法处理
- 除零处理
- 200 字符表达式长度限制

结果使用 Python 的 `int` 或 `float`。数学结果为整数时会返回整数，例如 `8/2` 返回 `4`；其他浮点结果遵循 Python 浮点数精度。

## Database

本地开发使用项目根目录下的 `calculator.db`。该文件在应用启动时自动创建，并已由 `.gitignore` 排除，不应提交到版本控制。

SQLAlchemy 表 `calculation_history` 包含：

- `id`：整数主键和索引。
- `expression`：非空表达式文本。
- `result`：非空 JSON 数值，读取后保持 `int` 或 `float`。
- `created_at`：非空 UTC 创建时间。

应用启动时通过 `Base.metadata.create_all()` 创建缺失的数据表。每个 HTTP 请求通过 `get_db()` 获取独立 Session，并在请求结束后关闭。写操作使用 `add`、`commit`、`refresh`，数据库异常时执行 `rollback`。

可通过环境变量覆盖默认数据库连接：

```powershell
$env:DATABASE_URL = "sqlite:///./custom-calculator.db"
uvicorn src.main:app
```

该入口也为后续部署更换数据库保留配置空间；Phase 5 不包含 PostgreSQL 迁移。

## 自动测试

```bash
pytest
```

测试覆盖基础运算、完整表达式解析、历史保存与排序、无效计算不保存、删除、缺失记录、数值类型和文件数据库持久化。

pytest 使用临时目录中的独立 SQLite 数据库，并通过 FastAPI dependency override 替换开发 Session，因此不会创建或污染项目根目录下的 `calculator.db`。

## 后续规划

下一阶段将进行 Frontend - Backend Integration。

用户登录、分页、搜索、收藏、Clear All、公网部署和 PostgreSQL 迁移不属于当前 Phase 5 的实现范围。
