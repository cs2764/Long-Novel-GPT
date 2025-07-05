# Windows 故障排除指南

## 常见启动错误及解决方案

### 1. 提示词文件路径错误

**错误信息**: 
```
FileNotFoundError: [Errno 2] No such file or directory: 'prompts/创作章节\\新建章节.txt'
```

**原因**: Windows和Unix系统的路径分隔符不同导致的路径问题。

**解决方案**:
1. 确保从项目根目录启动后端服务：
   ```cmd
   cd /d E:\Long-Novel-GPT
   conda activate long-novel-gpt
   cd backend
   python app.py
   ```

2. 如果仍有问题，检查项目目录结构：
   ```cmd
   dir prompts\创作章节\
   ```
   
   应该显示以下文件：
   - 新建章节.txt
   - 扩写章节.txt
   - 润色章节.txt
   - 等等

### 2. .env 文件未找到警告

**警告信息**: 
```
Warning: .env file not found
```

**解决方案**:
1. 复制环境配置模板：
   ```cmd
   copy .env.example .env
   ```

2. 编辑 `.env` 文件，配置至少一个API密钥。

### 3. Redis警告

**警告信息**: 
```
[WARNING] No redis installed, RedisRateLimiter unavailable
```

**说明**: 这是正常的警告，可以忽略。Redis用于分布式环境的速率限制，本地开发不需要。

### 4. 动态配置API注册成功

**成功信息**: 
```
✅ 动态配置API已注册
```

**说明**: 这表示新的配置系统已成功加载，可以通过Web界面管理AI提供商配置。

## 完整启动流程

### 使用批处理脚本（推荐）
```cmd
start_local_simple.bat
```

### 手动启动
```cmd
# 1. 激活conda环境
conda activate long-novel-gpt

# 2. 启动后端（新命令窗口）
cd /d E:\Long-Novel-GPT\backend
python app.py

# 3. 启动前端（另一个新命令窗口）
cd /d E:\Long-Novel-GPT
python frontend_server.py
```

## 验证启动成功

1. **后端健康检查**:
   浏览器访问: http://localhost:7869/health

2. **前端页面**:
   浏览器访问: http://localhost:8080

3. **配置API可用性**:
   浏览器访问: http://localhost:7869/api/providers

## 高级配置

### 使用新的动态配置系统

1. 在前端页面点击设置按钮
2. 切换到"AI提供商"标签
3. 选择要配置的提供商
4. 填入API密钥和其他配置
5. 测试连接
6. 保存配置

### 配置文件位置

- **运行时配置**: `runtime_config.json` (自动生成)
- **环境配置**: `.env` (需要手动创建)
- **Windows配置**: `LocalSettings.json` (浏览器本地存储)

## 获取帮助

如果遇到其他问题：

1. 查看详细错误信息
2. 检查文件路径是否正确
3. 确认conda环境已激活
4. 参考本项目的其他文档:
   - `Windows开发指南.md`
   - `Windows启动脚本说明.md`
   - `本地开发指南.md`

## 日志调试

启用详细日志：
```cmd
set DEBUG=1
python app.py
```

这将显示更多调试信息，有助于定位问题。