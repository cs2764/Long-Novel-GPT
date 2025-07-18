# 代码贡献指南

欢迎为Long-Novel-GPT项目贡献代码！本指南将帮助您了解如何参与项目开发，提交高质量的代码贡献。

## 📋 目录

1. [开始贡献](#开始贡献)
2. [开发环境设置](#开发环境设置)
3. [代码规范](#代码规范)
4. [提交流程](#提交流程)
5. [代码审查](#代码审查)
6. [文档贡献](#文档贡献)
7. [测试要求](#测试要求)
8. [发布流程](#发布流程)
9. [社区准则](#社区准则)
10. [常见问题](#常见问题)

## 开始贡献

### 1. 项目概述

Long-Novel-GPT是一个基于AI的长篇小说生成系统，支持多AI提供商、动态配置管理、完整的Web界面等功能。

**主要技术栈**：
- **后端**: Python, Flask, MongoDB, Redis
- **前端**: HTML, CSS, JavaScript, Nginx
- **AI集成**: OpenAI, DeepSeek, 阿里通义千问, 智谱AI等
- **部署**: Docker, Gunicorn

### 2. 贡献类型

我们欢迎以下类型的贡献：

- **Bug修复**: 修复已知问题
- **新功能**: 添加新的功能特性
- **性能优化**: 改进系统性能
- **文档改进**: 完善文档内容
- **测试增强**: 增加测试覆盖率
- **代码重构**: 改进代码结构
- **UI/UX改进**: 优化用户界面体验

### 3. 贡献前的准备

在开始贡献之前，请：

1. **阅读项目文档**: 了解项目架构和功能
2. **查看Issues**: 检查是否有相关的问题报告
3. **加入讨论**: 在Issue中讨论您的想法
4. **Fork项目**: 创建您自己的项目分支

## 开发环境设置

### 1. 系统要求

- **Python**: 3.8+
- **Node.js**: 16+ (如需前端开发)
- **Git**: 最新版本
- **Docker**: 可选，用于容器化部署

### 2. 环境配置

```bash
# 1. Fork并克隆项目
git clone https://github.com/your-username/Long-Novel-GPT.git
cd Long-Novel-GPT

# 2. 添加upstream远程仓库
git remote add upstream https://github.com/original-owner/Long-Novel-GPT.git

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 4. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. 安装pre-commit钩子
pre-commit install
```

### 3. 开发工具配置

**推荐IDE设置**：

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": false,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".coverage": true,
    "htmlcov": true
  }
}
```

## 代码规范

### 1. Python代码规范

我们遵循PEP 8标准，并使用以下工具：

```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码检查
flake8 .

# 类型检查
mypy core/ llm_api/
```

**代码风格示例**：

```python
# 好的代码风格
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class NovelWriter:
    """小说写作器类
    
    负责生成和处理小说内容
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """生成文本内容
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大token数量
            
        Returns:
            生成的文本内容，失败时返回None
            
        Raises:
            ValueError: 当prompt为空时抛出
        """
        if not prompt.strip():
            raise ValueError("提示词不能为空")
        
        try:
            # 生成逻辑
            result = self._call_api(prompt, max_tokens)
            self.logger.info(f"文本生成成功，长度: {len(result)}")
            return result
        except Exception as e:
            self.logger.error(f"文本生成失败: {e}")
            return None
    
    def _call_api(self, prompt: str, max_tokens: int) -> str:
        """调用API的私有方法"""
        # 实现细节
        pass
```

### 2. 文档字符串规范

```python
def process_chunks(
    chunks: List[Tuple[str, str]], 
    model_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """处理文本块列表
    
    将原始文本块转换为结构化数据，支持批量处理和错误恢复。
    
    Args:
        chunks: 文本块列表，每个元素为(标题, 内容)元组
        model_config: 模型配置字典，包含API密钥等信息
        
    Returns:
        处理后的数据列表，每个元素包含:
        - title: 标题
        - content: 处理后的内容
        - metadata: 元数据信息
        
    Raises:
        ValueError: 当chunks为空时
        APIError: 当API调用失败时
        
    Example:
        >>> chunks = [("第一章", "内容1"), ("第二章", "内容2")]
        >>> config = {"api_key": "your-key", "model": "gpt-3.5-turbo"}
        >>> result = process_chunks(chunks, config)
        >>> len(result)
        2
    """
```

### 3. 错误处理规范

```python
# 好的错误处理
import traceback
from typing import Optional

class APIError(Exception):
    """API调用错误"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

def safe_api_call(url: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """安全的API调用"""
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"API调用超时: {url}")
        raise APIError("API调用超时", 408)
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP错误: {e}")
        raise APIError(f"HTTP错误: {e}", e.response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {e}")
        raise APIError(f"请求失败: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        logger.error(traceback.format_exc())
        raise APIError(f"未知错误: {e}")
```

### 4. 前端代码规范

```javascript
// 好的JavaScript代码风格
class NovelGenerator {
    constructor(config) {
        this.config = config;
        this.isGenerating = false;
        this.currentStreamId = null;
    }
    
    /**
     * 生成小说内容
     * @param {string} prompt - 提示词
     * @param {Object} options - 选项参数
     * @returns {Promise<string>} 生成的内容
     */
    async generateNovel(prompt, options = {}) {
        if (!prompt || !prompt.trim()) {
            throw new Error('提示词不能为空');
        }
        
        if (this.isGenerating) {
            throw new Error('正在生成中，请稍后');
        }
        
        this.isGenerating = true;
        
        try {
            const response = await this.callAPI(prompt, options);
            return this.processResponse(response);
        } catch (error) {
            console.error('生成失败:', error);
            throw error;
        } finally {
            this.isGenerating = false;
        }
    }
    
    /**
     * 调用后端API
     * @private
     */
    async callAPI(prompt, options) {
        const requestData = {
            prompt_content: prompt,
            ...options
        };
        
        const response = await fetch('/api/write', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });
        
        if (!response.ok) {
            throw new Error(`API调用失败: ${response.status}`);
        }
        
        return response;
    }
}

// 使用示例
const generator = new NovelGenerator({
    model: 'gpt-4',
    maxTokens: 2000
});

generator.generateNovel('创作一个科幻故事')
    .then(content => {
        console.log('生成成功:', content);
    })
    .catch(error => {
        console.error('生成失败:', error);
    });
```

## 提交流程

### 1. 分支策略

我们使用Git Flow分支模型：

```bash
# 主要分支
main        # 生产分支，稳定版本
dev         # 开发分支，最新功能
hotfix/*    # 热修复分支
feature/*   # 功能分支
release/*   # 发布分支
```

### 2. 功能开发流程

```bash
# 1. 确保本地代码是最新的
git checkout dev
git pull upstream dev

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发功能
# 编写代码...

# 4. 提交代码
git add .
git commit -m "feat: 添加新功能描述"

# 5. 推送分支
git push origin feature/your-feature-name

# 6. 创建Pull Request
# 通过GitHub界面创建PR
```

### 3. 提交信息规范

我们使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```bash
# 格式
<type>(<scope>): <description>

# 类型
feat:     新功能
fix:      Bug修复
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(api): 添加OpenAI API支持
fix(ui): 修复设置页面显示错误
docs(readme): 更新安装说明
test(core): 添加writer模块单元测试
```

### 4. Pull Request模板

```markdown
## 📝 变更描述

请简要描述这次变更的内容：

- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他：

## 🔗 相关Issue

关联的Issue编号：#

## 📋 测试清单

- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成
- [ ] 文档已更新

## 🖼️ 截图（如适用）

如果是UI相关的变更，请提供截图。

## 📚 附加说明

有其他需要说明的内容吗？
```

## 代码审查

### 1. 审查标准

**代码质量**：
- [ ] 代码逻辑清晰
- [ ] 变量命名有意义
- [ ] 函数功能单一
- [ ] 错误处理完善
- [ ] 性能考虑充分

**测试覆盖**：
- [ ] 单元测试完整
- [ ] 边界条件测试
- [ ] 错误处理测试
- [ ] 性能测试（如需要）

**文档完整性**：
- [ ] 函数文档字符串
- [ ] 复杂逻辑注释
- [ ] API文档更新
- [ ] 使用示例

### 2. 审查流程

1. **自动检查**：CI/CD系统自动运行测试
2. **代码审查**：至少一名维护者审查代码
3. **测试验证**：审查者验证功能正常工作
4. **文档检查**：确保文档与代码同步更新
5. **合并决定**：维护者决定是否合并

### 3. 审查指导

**作为代码提交者**：
- 确保代码符合项目规范
- 提供清晰的PR描述
- 积极响应审查反馈
- 及时更新代码

**作为代码审查者**：
- 仔细阅读代码逻辑
- 检查测试覆盖率
- 验证功能正确性
- 提供建设性反馈

## 文档贡献

### 1. 文档类型

**技术文档**：
- API文档
- 架构设计文档
- 部署指南
- 开发指南

**用户文档**：
- 使用说明
- 快速开始指南
- 常见问题解答
- 故障排除指南

### 2. 文档写作规范

```markdown
# 文档标题

简要描述文档内容和目的。

## 📋 目录

1. [章节1](#章节1)
2. [章节2](#章节2)
3. [章节3](#章节3)

## 章节1

### 小节1.1

详细内容说明。

**代码示例**：

```python
# 代码示例
def example_function():
    return "Hello, World!"
```

**注意事项**：

⚠️ 重要提醒信息

💡 有用的提示

✅ 正确的做法

❌ 错误的做法

## 参考资料

- [相关链接1](https://example.com)
- [相关链接2](https://example.com)

---

*本文档最后更新：2024-01-01*
```

### 3. 文档更新流程

1. **确定需求**：识别需要更新的文档
2. **创建分支**：创建`docs/update-xxx`分支
3. **编写内容**：按照规范编写文档
4. **审查验证**：确保内容准确性
5. **提交PR**：提交Pull Request
6. **合并发布**：合并到主分支

## 测试要求

### 1. 测试类型

**单元测试**：
- 测试单个函数或方法
- 覆盖正常和异常情况
- 使用Mock隔离外部依赖

**集成测试**：
- 测试模块间交互
- 验证API端点功能
- 测试数据库操作

**端到端测试**：
- 测试完整用户流程
- 验证界面功能
- 测试跨浏览器兼容性

### 2. 测试编写要求

```python
# 测试文件命名：test_*.py
# 测试类命名：Test*
# 测试方法命名：test_*

import pytest
from unittest.mock import Mock, patch

class TestNovelWriter:
    """小说写作器测试类"""
    
    def test_generate_text_with_valid_prompt(self):
        """测试有效提示词的文本生成"""
        writer = NovelWriter(config={'api_key': 'test'})
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'text': '生成的内容'}
            
            result = writer.generate_text('测试提示词')
            
            assert result == '生成的内容'
            mock_post.assert_called_once()
    
    def test_generate_text_with_empty_prompt(self):
        """测试空提示词的错误处理"""
        writer = NovelWriter(config={'api_key': 'test'})
        
        with pytest.raises(ValueError, match="提示词不能为空"):
            writer.generate_text('')
    
    @pytest.mark.parametrize("prompt,expected", [
        ("短提示词", "短内容"),
        ("长提示词" * 100, "长内容"),
    ])
    def test_generate_text_with_different_lengths(self, prompt, expected):
        """测试不同长度提示词的处理"""
        writer = NovelWriter(config={'api_key': 'test'})
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'text': expected}
            
            result = writer.generate_text(prompt)
            
            assert result == expected
```

### 3. 测试运行

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_writer.py

# 运行特定测试类
pytest tests/test_writer.py::TestNovelWriter

# 运行特定测试方法
pytest tests/test_writer.py::TestNovelWriter::test_generate_text

# 运行测试并生成覆盖率报告
pytest --cov=core --cov-report=html

# 运行性能测试
pytest --benchmark-only
```

## 发布流程

### 1. 版本管理

我们使用[语义化版本](https://semver.org/)：

```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的API变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的Bug修复
```

### 2. 发布准备

```bash
# 1. 确保所有测试通过
pytest

# 2. 更新版本号
python scripts/bump_version.py --version 1.2.3

# 3. 更新变更日志
python scripts/update_changelog.py

# 4. 提交版本更新
git add .
git commit -m "chore: 发布版本 1.2.3"

# 5. 创建标签
git tag -a v1.2.3 -m "Release v1.2.3"

# 6. 推送到远程
git push origin main --tags
```

### 3. 发布检查清单

- [ ] 所有测试通过
- [ ] 代码覆盖率达标
- [ ] 文档已更新
- [ ] 变更日志完整
- [ ] 版本号正确
- [ ] 依赖项更新
- [ ] 安全检查通过

## 社区准则

### 1. 行为准则

我们致力于为每个人创造一个友好、安全的社区环境：

- **尊重他人**：尊重不同观点和经验
- **包容性**：欢迎所有背景的贡献者
- **建设性**：提供有帮助的反馈
- **专业性**：保持专业和礼貌的交流
- **协作性**：支持团队合作

### 2. 沟通方式

**GitHub Issues**：
- 报告Bug
- 提出功能请求
- 讨论设计决策

**Pull Requests**：
- 代码审查
- 技术讨论
- 实现细节

**讨论区**：
- 一般性问题
- 经验分享
- 社区互动

### 3. 冲突解决

如果遇到冲突或不当行为：

1. **直接沟通**：尝试私下解决
2. **寻求帮助**：联系项目维护者
3. **报告问题**：通过邮件报告严重问题
4. **社区支持**：寻求社区成员帮助

## 常见问题

### Q: 如何选择合适的Issue开始贡献？

A: 建议从以下类型开始：
- 标记为`good first issue`的问题
- 文档改进类问题
- 小的Bug修复
- 测试用例添加

### Q: 如何设置开发环境？

A: 参考[快速开发指南](QUICK_DEVELOPMENT.md)获取详细步骤。

### Q: 代码审查需要多长时间？

A: 通常在3-7个工作日内完成。复杂的PR可能需要更长时间。

### Q: 如何处理审查意见？

A: 
1. 仔细阅读反馈
2. 如有疑问，积极沟通
3. 及时修改代码
4. 更新PR描述

### Q: 贡献代码是否需要签署CLA？

A: 目前不需要，但我们可能在将来引入CLA。

### Q: 如何成为项目维护者？

A: 通过持续的高质量贡献、积极参与社区讨论、帮助其他贡献者等方式展现能力。

## 资源链接

### 项目资源
- [项目主页](https://github.com/your-org/Long-Novel-GPT)
- [Issue跟踪](https://github.com/your-org/Long-Novel-GPT/issues)
- [项目文档](https://github.com/your-org/Long-Novel-GPT/tree/main/docs)

### 开发工具
- [Python代码风格指南](https://www.python.org/dev/peps/pep-0008/)
- [Git教程](https://git-scm.com/docs)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### 学习资源
- [Flask文档](https://flask.palletsprojects.com/)
- [pytest文档](https://docs.pytest.org/)
- [Docker文档](https://docs.docker.com/)

## 致谢

感谢所有为Long-Novel-GPT项目做出贡献的开发者们！您的努力使这个项目不断完善。

特别感谢：
- 核心维护者团队
- 活跃的社区成员
- 提供反馈的用户
- 文档贡献者

---

*本指南会根据项目发展持续更新。如有建议或疑问，请提交Issue或联系维护者。*

**开始您的贡献之旅吧！** 🚀 