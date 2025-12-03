# StrmConvert

一个用于监控源文件夹、转换 `.strm` 文件中的路径，并同步到目标文件夹的应用程序。提供简洁的网页界面，方便配置和管理。

## 功能特点

- **路径转换**：自动将 `.strm` 文件中的路径按照您设置的规则进行替换
- **文件夹同步**：保持源文件夹和目标文件夹的目录结构完全一致
- **实时监控**：自动监控源文件夹的变化，新增、修改或删除文件时立即同步
- **网页界面**：通过浏览器访问配置界面，轻松管理和控制
- **多配置支持**：可以同时配置多个源文件夹和目标文件夹的同步规则
- **仅同步模式**：可以将搜索字符串和替换字符串留空，实现纯文件夹同步而不进行路径转换

## Docker 安装

### 方式一：使用 Docker Compose（推荐）

编辑 `docker-compose.yml` 文件，添加您的源文件夹和目标文件夹挂载：
   ```yaml
   version: '3.8'
   
   services:
     strmconvert:
       build: .
       container_name: strmconvert
       restart: unless-stopped
       ports:
         - "9115:9115"
       volumes:
         # 挂载配置目录以持久化配置
         - ./config:/app/config
         # 在此挂载您的源文件夹和目标文件夹
         # - /path/to/your/source/folder:/mnt/source
         # - /path/to/your/target/folder:/mnt/target
       environment:
         - TZ=Asia/Shanghai
   ```

### 方式二：使用 Docker 命令

   ```bash
   docker run -d \
     --name strmconvert \
     -p 9115:9115 \
     -v $(pwd)/config:/app/config \
     -v /path/to/source:/mnt/source \
     -v /path/to/target:/mnt/target \
     --restart unless-stopped \
     strmconvert
   ```

## 访问网页界面

启动容器后，在浏览器中访问：

```
http://localhost:9115
```

## 配置说明

在网页界面中，点击"添加新记录"按钮，配置以下信息：

### 必填项

- **源文件夹**：包含 `.strm` 文件的文件夹路径
  - 在 Docker 中使用容器内路径，如：`/mnt/source`
  
- **目标文件夹**：转换后的文件保存路径
  - 在 Docker 中使用容器内路径，如：`/mnt/target`

### 可选项

- **搜索字符串**：要查找的字符串（`.strm` 文件中的第一个匹配项将被替换）
  - 留空表示仅同步文件，不进行路径转换
  
- **替换字符串**：替换后的字符串
  - 留空表示仅同步文件，不进行路径转换

### 操作说明

- **启动监控**：点击"启动监控"按钮，开始实时监控源文件夹
- **停止监控**：点击"停止监控"按钮，停止监控
- **全量同步**：点击"全量同步"按钮，立即同步所有文件
- **配置**：点击"配置"按钮，修改同步规则
- **删除**：点击"删除"按钮，删除同步规则

## 日志文件位置

日志文件保存在 `config/logs/` 目录下：

- **日志文件**：`config/logs/strmconvert.log`
- **日志轮转**：每天自动创建新的日志文件
- **保留期限**：自动保留最近 7 天的日志文件

在 Docker 部署中，由于 `./config` 目录已挂载到主机，您可以直接在主机上访问 `./config/logs/` 目录查看日志。

## 注意事项

- 在 Docker 容器中配置路径时，请使用容器内的挂载路径（如 `/mnt/source` 和 `/mnt/target`），而不是主机路径
- 程序只会替换每个 `.strm` 文件中第一个匹配的字符串
- 如果搜索字符串为空，`.strm` 文件将不会被转换，直接原样复制
- 确保目标文件夹有写入权限
- Docker 部署时，请确保挂载的文件夹有正确的权限
