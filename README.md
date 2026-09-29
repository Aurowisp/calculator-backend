# Calculator Backend

## 项目介绍

这是前后端分离计算器系统的 Backend，使用分层结构组织代码。

当前为 Phase 2 - Backend Foundation，仅建立后端工程基础框架。此阶段不包含四则运算、表达式解析、数据库或历史记录功能。

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
│   ├── calculator/                # 未来的表达式解析与执行模块
│   │   ├── parser.py
│   │   └── evaluator.py
│   ├── model/                     # 未来的数据模型层
│   │   └── history.py
│   └── database/                  # 未来的数据库连接层
│       └── database.py
├── requirements.txt
├── README.md
├── codestyle.md
└── .gitignore
```

各 Python 子目录均包含 `__init__.py`，以便作为独立包导入。

### 分层职责

- `controller`：接收 HTTP 请求并定义 API 路由。
- `service`：未来用于编排业务用例，避免业务逻辑进入 Controller。
- `calculator`：未来用于表达式解析和计算执行。
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

## API 测试

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

## 后续规划

后续阶段将逐步增加：

- Calculate API
- Expression parser
- Database history

这些功能不属于当前 Phase 2 的实现范围。
