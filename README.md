# Calculator Backend

## 项目介绍

这是前后端分离计算器系统的 Backend，使用分层结构组织代码。

当前为 Phase 3 - Implement Calculate API。后端已提供安全的基础四则运算接口；数据库和历史记录功能尚未实现。

## 技术栈

- Python 3.x
- FastAPI
- Uvicorn

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
│   ├── model/                     # API 数据模型和未来的持久化模型
│   │   ├── calculation.py
│   │   └── history.py
│   └── database/                  # 未来的数据库连接层
│       └── database.py
├── requirements.txt
├── README.md
├── codestyle.md
├── tests/
│   └── test_calculate_api.py
└── .gitignore
```

各 Python 子目录均包含 `__init__.py`，以便作为独立包导入。

### 分层职责

- `controller`：接收 HTTP 请求并定义 API 路由。
- `service`：未来用于编排业务用例，避免业务逻辑进入 Controller。
- `calculator`：负责安全的表达式解析和计算执行，不依赖 FastAPI。
- `model`：未来用于定义 History 等数据模型。
- `database`：未来用于配置和管理 SQLite 连接。

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

无效表达式返回 `400 Bad Request`：

```json
{
  "success": false,
  "message": "Invalid expression"
}
```

缺失字段或字段类型错误由 FastAPI/Pydantic 返回 `422 Unprocessable Entity`。

核心计算全部由后端完成。解析器不会使用 `eval()`、`exec()`、`compile()`，也不会把用户表达式作为 Python 程序执行。Phase 3 支持整数、基础四则运算和运算符优先级。

## 自动测试

```bash
pytest
```

测试覆盖加、减、乘、除、除零、空表达式、非法字符、非法表达式和请求模型校验。

## 后续规划

后续阶段将逐步增加：

- 完整 Expression parser（括号、小数、一元正负号）
- Database history

数据库、历史记录 API、持久化和部署不属于当前 Phase 3 的实现范围。
