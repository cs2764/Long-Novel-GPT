<h1 align="center">Long-Novel-GPT Enhanced</h1>

<p align="center">
  AI一键生成长篇小说 - 增强版
</p>

<p align="center">
  <a href="#关于项目">关于项目</a> •
  <a href="#版本信息">版本信息</a> •
  <a href="#新增功能">新增功能</a> •
  <a href="#更新日志">更新日志</a> •
  <a href="#小说生成prompt">小说生成Prompt</a> •
  <a href="#快速上手">快速上手</a> •
  <a href="#demo使用指南">Demo使用指南</a> •
  <a href="#开发文档">开发文档</a>
</p>

<hr>

<h2 id="关于项目">🎯 关于项目</h2>

本项目是基于 [MaoXiaoYuZ/Long-Novel-GPT](https://github.com/MaoXiaoYuZ/Long-Novel-GPT) 的二次开发增强版本。

**原始项目**: Long-Novel-GPT 是一个基于LLM和RAG的长篇小说Agent，根据用户的提问（要写什么小说，要对什么情节做出什么改动）LNGPT会调用工具检索相关正文片段和剧情纲要，并且对相关正文片段进行修改，同时更新剧情纲要。

**增强版本**: 在原有功能基础上，增加了动态配置系统、多API提供商支持、完善的本地运行环境、详细的API调试日志等功能。

> 💡 **开发声明**: 本项目的所有代码、文档和功能增强均由 Claude Code 生成和开发。

<p align="center">
  <img src="assets/Long-Novel-Agent.jpg" alt="Long Novel Agent Architecture" width="600"/>
</p>

1. 从本地导入现有小说
2. 拆书（提取剧情人物关系，生成剧情纲要）
3. 输入你的意见
4. 检索相关正文片段和剧情纲要
5. 对正文片段进行修改
6. 同步更新剧情纲要


<h2 id="版本信息">📋 版本信息</h2>

**当前版本**: v3.0.0 Enhanced Edition
**基于**: MaoXiaoYuZ/Long-Novel-GPT v2.2
**开发工具**: Claude Code
**发布日期**: 2025年1月

<h2 id="新增功能">✨ 新增功能</h2>

### 🚀 动态配置系统
- **多API提供商支持**: OpenRouter、文心一言、豆包、智谱AI、LM Studio等
- **实时模型列表获取**: 从各API提供商动态获取最新模型列表
- **配置热更新**: 无需重启即可更新API配置
- **统一配置管理**: 所有API配置集中管理

### 🔧 本地运行环境
- **简化启动脚本**: Windows一键启动，自动处理依赖和环境
- **跨平台支持**: 完善的Python启动器，支持Windows、macOS、Linux
- **自动浏览器打开**: 服务启动后自动打开浏览器
- **智能端口管理**: 自动检测和分配可用端口

### 📊 调试和监控
- **详细API日志**: 显示完整的HTTP请求和响应信息
- **实时错误追踪**: 完整的错误堆栈和调试信息
- **性能监控**: API调用时间统计和响应分析
- **成本跟踪**: 实时显示API调用费用

### 🌐 OpenRouter 集成
- **无需API Key的模型列表**: 直接从OpenRouter获取模型列表
- **智能模型过滤**: 支持按提供商筛选模型（OpenAI、Google、Qwen、DeepSeek、Grok等）
- **模型详情展示**: 显示模型上下文长度、价格等详细信息
- **实时可用性检测**: 检测模型当前可用状态

详细开发文档请参考 [开发文档](#开发文档) 部分。

<h2 id="更新日志">📅 更新日志</h2>

### 🎉 Long-Novel-GPT 3.0.0 Enhanced Edition
- 🚀 全新动态配置系统，支持多API提供商
- 🔧 简化本地运行环境，一键启动
- 📊 完善的API调试日志系统
- 🌐 OpenRouter深度集成
- 💻 改进的Windows启动脚本
- 🛠️ 统一的配置管理界面
- 📈 实时性能监控和成本追踪

### 🎉 Long-Novel-GPT 2.2 更新
- 支持查看Prompt
- **支持导入小说，在已有的小说基础上进行改写**
- 支持在**设置**中选择模型
- 支持在创作时实时**显示调用费用**

<p align="center">
  <img src="assets/book-select.jpg" alt="支持在已有的小说基础上进行改写" width="600"/>
</p>

### 🎉 Long-Novel-GPT 2.1 更新
- 支持选择和创作章节

### 🎉 Long-Novel-GPT 2.0 更新
- 提供全新的UI界面


### 🔮 后续更新计划
- 考虑一个更美观更实用的编辑界面（已完成）
- 支持文心 Novel 模型（已完成）
- 支持豆包模型（已完成）
- 通过一个创意直接一键生成完整长篇小说（进行中）
- 支持生成大纲和章节（进行中）


<h2 id="小说生成prompt">📚 小说生成 Prompt</h2>

| Prompt | 描述 |
|--------|------|
| [天蚕土豆风格](custom/根据提纲创作正文/天蚕土豆风格.txt) | 用于根据提纲创作正文，模仿天蚕土豆的写作风格 |
| [对草稿进行润色](custom/根据提纲创作正文/对草稿进行润色.txt) | 对你写的网文初稿进行润色和改进 |

[📝 提交你的 Prompt](https://github.com/MaoXiaoYuZ/Long-Novel-GPT/issues/new?assignees=&labels=prompt&template=custom_prompt.md&title=新的Prompt)

<h2 id="快速上手">🚀 快速上手</h2>

### Docker一键部署

运行下面命令拉取long-novel-gpt镜像
```bash
docker pull maoxiaoyuz/long-novel-gpt:latest
```

下载或复制[.env.example](.env.example)文件，将其放在你的任意一个目录下，将其改名为 **.env**, 并根据文件中提示填写API设置。

填写完成后在该 **.env**文件目录下，运行以下命令：
```bash
docker run -p 80:80 --env-file .env -d maoxiaoyuz/long-novel-gpt:latest
```
**注意，如果你在启动后改动了.env文件，那么必须关闭已启动的容器后，再运行上述命令才行。**

接下来访问 http://localhost 即可使用，如果是部署在服务器上，则访问你的服务器公网地址即可。


<p align="center">
  <img src="assets/LNGPT-V2.0.png" alt="Gradio DEMO有5个Tab页面" width="600"/>
</p>

### 使用本地的大模型服务
要使用本地的大模型服务，只需要在Docker部署时额外注意以下两点。

第一，启动Docker的命令需要添加额外参数，具体如下：
```bash
docker run -p 80:80 --env-file .env -d --add-host=host.docker.internal:host-gateway maoxiaoyuz/long-novel-gpt:latest
```

第二，将本地的大模型服务暴露为OpenAI格式接口，在[.env.example](.env.example)文件中进行配置，同时GPT_BASE_URL中localhost或127.0.0.1需要替换为：**host.docker.internal**
例如
```
# 这里GPT_BASE_URL格式只提供参考，主要是替换localhost或127.0.0.1
# 可用的模型名可以填1个或多个，用英文逗号分隔
LOCAL_BASE_URL=http://host.docker.internal:7777/v1
LOCAL_API_KEY=you_api_key
LOCAL_AVAILABLE_MODELS=model_name1,model_name2
# 只有一个模型就只写一个模型名，多个模型要用英文逗号分割
```

<h2 id="demo使用指南">🖥️ Demo 使用指南</h2>

### 当前Demo能生成百万字小说吗？
Long-Novel-GPT-2.1版本完全支持生成百万级别小说的版本，而且是多窗口同步生成，速度非常快。

同时你可以自由控制你需要生成的部分，对选中部分重新生成等等。

而且，Long-Novel-GPT-2.1会自动管理上下文，在控制API调用费用的同时确保了生成剧情的连续。

在2.1版本中，你需要部署在本地并采用自己的API-Key，在[.env.example](.env.example)文件中配置生成时采用的最大线程数。
```
# Thread Configuration - 线程配置
# 生成时采用的最大线程数
MAX_THREAD_NUM=5
```
在线Demo是不行的，因为最大线程为5。

### 如何利用LN-GPT-2.1生成百万字小说？
首先，你需要部署在本地，配置API-Key并解除线程限制。

然后，在**创作章节**阶段，创作50章，每章200字。（50+线程并行）

其次，在**创作剧情**阶段，将每章的200字扩充到1k字。

最后，在**创作正文**阶段，将每章的1K字扩充到2k字，这一步主要是润色文本和描写。

一共，50 * 2k = 100k (十万字)。

**创作章节支持创作无限长度的章节数，同理，剧情和正文均不限长度，LNGPT会自动进行切分，自动加入上下文，并自动采取多个线程同时创作。**

### LN-GPT-2.1生成的百万字小说怎么样？
总的来说，2.1版本能够实现在用户监督下生成达到签约门槛的网文。

而且，我们的最终目标始终是实现一键生成全书，将在2-3个版本迭代后正式推出。

<h2 id="开发文档">📖 开发文档</h2>

### 🔧 技术架构文档
- [🏗️ 动态配置系统设计](docs/DYNAMIC_CONFIG_SYSTEM.md) - 详细介绍多API提供商动态配置架构
- [🚀 启动器系统设计](docs/LAUNCHER_SYSTEM.md) - 跨平台启动器实现原理
- [📊 API调试日志系统](docs/API_LOGGING_SYSTEM.md) - 完整的API调试和监控系统

### 🌐 OpenRouter 集成文档
- [🔌 OpenRouter API集成指南](docs/OPENROUTER_INTEGRATION.md) - OpenRouter API调用详细说明
- [📋 模型列表获取和过滤](docs/MODEL_FILTERING.md) - 模型列表API和过滤机制
- [🎯 API响应数据结构](docs/API_RESPONSE_STRUCTURE.md) - OpenRouter API响应格式详解

### 💻 部署和配置文档
- [⚙️ 环境配置指南](docs/ENVIRONMENT_SETUP.md) - 完整的环境配置步骤
- [🔧 API配置管理](docs/API_CONFIGURATION.md) - 各API提供商配置说明
- [🐛 调试和故障排除](docs/DEBUGGING_GUIDE.md) - 常见问题解决方案

### 🛠️ 开发指南
- [🏃 快速开发指南](docs/QUICK_DEVELOPMENT.md) - 开发环境搭建和调试
- [🧪 测试和验证](docs/TESTING_GUIDE.md) - 功能测试和API验证
- [🔄 代码贡献指南](docs/CONTRIBUTION_GUIDE.md) - 代码提交和开发规范

> 📝 **注意**: 以上所有文档均由 Claude Code 自动生成，确保文档与代码实现保持同步。
