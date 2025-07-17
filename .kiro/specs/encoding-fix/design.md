# Design Document

## Overview

本设计文档描述了如何修复DBCat应用程序中的编码问题。主要问题是在Windows平台上，当应用程序读取SQL文件时没有明确指定编码格式，导致Python使用系统默认的GBK编码尝试解码UTF-8文件内容，从而引发UnicodeDecodeError。

## Architecture

### 问题分析

1. **根本原因**: `DBCat/sql_editor.py` 第37行的文件读取操作没有指定编码格式
   ```python
   with open(file, 'r') as fileHandler:  # 缺少encoding参数
   ```

2. **影响范围**: 
   - SQL文件加载功能
   - 配置文件读取功能
   - 任何涉及文本文件读写的操作

3. **系统行为**: 
   - 在Windows上，Python默认使用系统编码(通常是GBK)
   - 当遇到UTF-8编码的文件时，GBK解码器无法处理某些字节序列

### 解决方案架构

采用统一的文件编码处理策略：

1. **标准化编码**: 所有文本文件操作统一使用UTF-8编码
2. **错误处理**: 实现优雅的编码错误处理机制
3. **向后兼容**: 支持读取可能存在的旧编码文件

## Components and Interfaces

### 1. 文件读取组件 (File Reading Component)

**位置**: `DBCat/sql_editor.py`

**修改点**:
- `initSqlEdit()` 方法中的文件读取操作
- 添加编码错误处理逻辑

**接口设计**:
```python
def safe_read_file(file_path: Path) -> str:
    """
    安全读取文件内容，支持多种编码格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容字符串
        
    Raises:
        FileReadError: 当文件无法读取时
    """
```

### 2. 文件写入组件 (File Writing Component)

**位置**: `DBCat/sql_editor.py`, `DBCat/resource.py`

**修改点**:
- 确保所有文件写入操作都明确指定UTF-8编码
- `resource.py` 中的配置文件写入

### 3. 错误处理组件 (Error Handling Component)

**功能**:
- 捕获和处理编码相关异常
- 提供用户友好的错误信息
- 记录详细的错误日志

## Data Models

### 编码处理策略

```python
ENCODING_STRATEGIES = [
    'utf-8',           # 首选编码
    'utf-8-sig',       # 带BOM的UTF-8
    'gbk',             # Windows中文编码
    'cp1252',          # Windows西文编码
    'latin1'           # 最后备选
]
```

### 错误信息模型

```python
class FileEncodingError(Exception):
    def __init__(self, file_path: str, attempted_encodings: list, original_error: Exception):
        self.file_path = file_path
        self.attempted_encodings = attempted_encodings
        self.original_error = original_error
        super().__init__(f"无法读取文件 {file_path}，尝试的编码: {attempted_encodings}")
```

## Error Handling

### 1. 编码检测和回退机制

```python
def read_file_with_encoding_detection(file_path):
    for encoding in ENCODING_STRATEGIES:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise FileEncodingError(file_path, ENCODING_STRATEGIES, None)
```

### 2. 用户友好的错误提示

- 当文件读取失败时，显示清晰的错误对话框
- 提供可能的解决方案建议
- 记录详细错误信息到日志文件

### 3. 优雅降级

- 如果无法读取某个SQL文件，跳过该文件但继续加载其他文件
- 在界面上显示加载失败的文件列表
- 允许用户手动重新加载失败的文件

## Testing Strategy

### 1. 单元测试

- 测试不同编码格式的文件读取
- 测试编码错误的处理逻辑
- 测试文件写入的编码正确性

### 2. 集成测试

- 测试应用程序启动时的文件加载过程
- 测试SQL文件的保存和加载循环
- 测试在不同Windows系统上的兼容性

### 3. 边界测试

- 测试空文件的处理
- 测试包含特殊字符的文件
- 测试文件权限问题的处理

### 4. 回归测试

- 确保修复不影响现有功能
- 测试中文字符的正确显示
- 验证文件保存格式的一致性

## Implementation Notes

### 关键修改点

1. **DBCat/sql_editor.py**:
   - 第37行: 添加 `encoding='utf-8'` 参数
   - 添加编码错误处理逻辑
   - 实现多编码尝试机制

2. **DBCat/resource.py**:
   - 第30行: 确保配置文件写入使用UTF-8编码
   - 添加文件操作的错误处理

3. **错误日志**:
   - 添加编码相关错误的详细日志记录
   - 帮助用户和开发者诊断问题

### 性能考虑

- 编码检测只在文件读取失败时进行，不影响正常情况下的性能
- 缓存成功的编码格式，避免重复检测
- 异步处理大文件的编码检测

### 兼容性保证

- 保持与现有SQL文件格式的兼容性
- 支持从旧版本应用程序迁移
- 确保跨平台文件交换的正确性