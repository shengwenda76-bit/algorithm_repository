# alg_tool Settings Design

## Goal

为可移植的 `alg_tool/` 增加集中式 `settings.py` 配置入口，并在 `publish.py` 中加入发布前配置完整性校验和远端连通性校验。算法开发者复制整个 `alg_tool/` 目录后，应能通过修改一个配置文件完成私有 PyPI 和平台注册配置，而不必依赖分散的环境变量。

## Scope

本次只覆盖 `alg_tool` 发布流程的配置管理与远端探测：

- 新增 `alg_tool/settings.py`
- 让 `publish.py` 统一读取配置
- 支持环境变量覆盖 `settings.py`
- 在上传和注册前执行配置完整性校验
- 在需要时执行仓库和平台注册地址连通性校验

本次不覆盖：

- `create_alg.py` 行为变更
- 平台注册协议改造
- 真正的凭据加密或密钥托管
- 更复杂的多环境配置分层

## Requirements

### Portability

`alg_tool` 仍然必须可整体复制到任意空目录中使用，不能依赖当前仓库的配置系统。`settings.py` 必须是 `alg_tool` 自带文件，复制后即可直接修改。

### Settings Source Order

配置读取顺序应为：

1. `alg_tool/settings.py` 中的默认配置
2. 同名环境变量覆盖

这样既方便本地直接使用，也保留了 CI 或特殊环境中的动态覆盖能力。

### Managed Settings

建议统一管理以下配置：

- `PYPI.REPOSITORY_URL`
- `PYPI.USERNAME`
- `PYPI.PASSWORD`
- `PYPI.TIMEOUT_SECONDS`
- `PYPI.VERIFY_SSL`
- `PLATFORM.REGISTER_URL`
- `PLATFORM.TOKEN`
- `PLATFORM.TIMEOUT_SECONDS`
- `VALIDATION.CHECK_REMOTE_CONNECTIVITY`

## Approaches

### Approach A: Only environment variables

优点：

- 实现最简单

缺点：

- 可读性差
- 对便携工具不友好
- 不符合“复制后开箱即用”的目标

### Approach B: settings.py plus environment overrides

优点：

- 本地体验最好
- 仍支持 CI 覆盖
- 结构清晰，便于文档说明

缺点：

- 需要维护一份额外配置模块

### Approach C: settings.py plus local overlay plus environment overrides

优点：

- 最灵活

缺点：

- 对当前一期来说过重
- 会增加便携工具的理解成本

## Recommended Design

采用 Approach B：`settings.py` 为主，环境变量覆盖。

### settings.py shape

`alg_tool/settings.py` 提供一个 `ALG_TOOL` 配置字典和一个轻量 dataclass：

- 配置字典负责表达默认值
- dataclass 负责给 `publish.py` 提供类型更明确的运行时对象

### publish.py flow

新的发布流程顺序为：

1. 读取本地算法包上下文
2. 加载并合并 `settings.py` 与环境变量
3. 校验本地算法包结构
4. 校验上传和注册配置是否完整
5. 如果启用远端检查，则探测仓库和平台注册地址
6. 运行测试
7. 构建包
8. 执行上传
9. 执行注册

### Validation rules

如果检测到以下情况，应在真正上传前就失败：

- 仓库上传被启用但缺少仓库地址、用户名或密码
- 平台注册被启用但缺少注册地址
- 平台注册被启用但没有可用于 artifact 的仓库地址

### Connectivity checks

远端检查应尽量轻量：

- PyPI 仓库地址：优先尝试 `HEAD`，失败时可退到 `GET`
- 平台注册地址：优先尝试 `HEAD`，失败时可退到 `GET`

连通性校验只负责回答“地址是否可达、响应是否正常”，不负责模拟完整上传或完整注册。

## Testing Strategy

采用 TDD，并优先覆盖：

- 默认配置能从 `settings.py` 读取
- 环境变量能覆盖 `settings.py`
- 上传配置不完整时会失败
- 注册配置不完整时会失败
- 远端检查开关开启时会执行探测
- 远端检查开关关闭时会跳过探测

## Risks

- 有些私有仓库或网关不支持 `HEAD`，因此需要提供 `GET` 回退
- 网络环境受限时，远端探测可能误判，因此必须允许通过配置关闭
- 把凭证写进 `settings.py` 适合“自己人”场景，但 README 需要明确提醒注意文件保管
