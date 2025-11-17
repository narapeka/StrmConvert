# StrmConvert

一个跨平台的 Python 应用程序，用于监控源文件夹、转换 `.strm` 文件中的路径，并同步到目标文件夹。提供简洁的网页界面，方便配置和管理。

## 功能简介

- **路径转换**：自动将 `.strm` 文件中的路径按照您设置的规则进行替换
- **文件夹同步**：保持源文件夹和目标文件夹的目录结构完全一致
- **实时监控**：自动监控源文件夹的变化，新增、修改或删除文件时立即同步
- **网页界面**：通过浏览器访问配置界面，轻松管理和控制
- **多配置支持**：可以同时配置多个源文件夹和目标文件夹的同步规则

## 安装和运行

### Windows 系统

1. 下载或克隆本项目到本地
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```
4. 打开浏览器访问：`http://localhost:9115`

### Linux 系统

#### 快速开始

1. 下载或克隆本项目到本地
2. 安装依赖包：
   ```bash
   pip3 install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python3 main.py
   ```
4. 打开浏览器访问：`http://localhost:9115`

#### 安装为系统服务（可选）

如果您希望程序在后台持续运行，可以安装为系统服务：

1. 赋予安装脚本执行权限：
   ```bash
   chmod +x install.sh
   ```

2. 以管理员权限运行安装脚本：
   ```bash
   sudo ./install.sh
   ```

   安装脚本会自动完成以下操作：
   - 安装程序文件到 `/opt/strmconvert`
   - 安装 Python 依赖包
   - 创建系统服务
   - **自动启用服务（开机自启）**
   - **自动启动服务**

3. 编辑配置文件（可选）：
   ```bash
   sudo nano /opt/strmconvert/config.yaml
   ```

4. 查看服务状态：
   ```bash
   sudo systemctl status strmconvert
   ```

5. 查看日志：
   ```bash
   sudo journalctl -u strmconvert -f
   ```

## 使用示例

### 示例 1：替换 URL 地址

假设您的 `.strm` 文件中包含 `http://192.168.1.50:3000`，需要替换为 `//nassss`：

```yaml
records:
  - source_folder: D:\strmtest\source
    target_folder: D:\strmtest\target
    search_string: http://192.168.1.50:3000
    replacement_string: //nassss
```

### 示例 2：转换绝对路径为相对路径

将 Linux 系统中的绝对路径转换为相对路径：

```yaml
records:
  - source_folder: /media/movies
    target_folder: /media/movies_converted
    search_string: /mnt/nas/media
    replacement_string: ../../nas/media
```

### 示例 3：Windows 路径转换

转换 Windows 系统中的路径：

```yaml
records:
  - source_folder: C:/Users/User/Videos
    target_folder: D:/Backup/Videos
    search_string: C:\\Users\\User
    replacement_string: D:\\Backup
```

### 示例 4：多个配置

您可以同时配置多个同步任务：

```yaml
records:
  - source_folder: /home/user/movies
    target_folder: /home/user/movies_converted
    search_string: /old/path
    replacement_string: /new/path
  - source_folder: /home/user/tv
    target_folder: /home/user/tv_converted
    search_string: /old/path
    replacement_string: /new/path
```

### 配置说明

- **source_folder**：源文件夹路径（包含 `.strm` 文件的文件夹，支持子文件夹）
- **target_folder**：目标文件夹路径（转换后的文件将保存到这里，保持相同的目录结构）
- **search_string**：要查找的字符串（`.strm` 文件中的第一个匹配项将被替换）
- **replacement_string**：替换后的字符串

### 使用网页界面

1. 运行程序后，在浏览器中打开 `http://localhost:9115`
2. 在配置页面编辑 `config.yaml` 文件内容
3. 点击"保存"按钮保存配置
4. 在控制面板中点击"开始监控"启动实时同步
5. 点击"执行同步"可以立即同步所有文件

### 注意事项

- Windows 系统可以使用正斜杠 `/` 或反斜杠 `\` 作为路径分隔符
- Linux 系统请使用正斜杠 `/`
- 程序只会替换每个 `.strm` 文件中第一个匹配的字符串
- 确保目标文件夹有写入权限
