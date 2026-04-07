# 视频剪辑工具

## 一、剪映专业版

### 快速开始
1. **下载**：剪映官网 (capcut.cn)
2. **安装**：Windows/Mac客户端
3. **新建项目**：选择分辨率和帧率

### 界面介绍
- **素材区**：导入和管理素材
- **预览区**：实时预览效果
- **时间轴**：编辑视频轨道
- **工具栏**：各种编辑工具

### 核心功能

#### 1. 素材导入
```
支持格式：MP4, MOV, AVI, MKV, JPG, PNG, MP3, WAV
导入方式：拖拽或 Ctrl+I
```

#### 2. 字幕处理
- **自动识别**：Ctrl+M
- **手动添加**：点击"T"添加文字
- **样式选择**：多种字幕模板
- **字体调整**：支持自定义字体

#### 3. 智能功能
| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 智能抠像 | Ctrl+E | 移除背景 |
| 智能字幕 | Ctrl+M | 识别配音 |
| AI特效 | - | 多种AI效果 |
| 关键帧 | Alt+K | 动画关键帧 |

#### 4. 音频处理
- **音量调节**：轨道上直接拖动
- **淡入淡出**：右键轨道 → 显示属性
- **分离音频**：右键片段 → 分离音频
- **降噪**：音频特效 → 降噪

#### 5. 导出设置
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 格式 | MP4 | 通用性强 |
| 编码 | H.264 | 兼容性最好 |
| 分辨率 | 1080P/4K | 根据需求 |
| 帧率 | 30fps/60fps | 运动场景用60fps |
| 码率 | 推荐8-16Mbps | 越高越清晰 |

### 工作流建议

```
1. 导入所有素材
2. 整理素材（标记、排序）
3. 粗剪：按脚本顺序排列
4. 精剪：调整片段长度
5. 添加字幕（AI识别+手动调整）
6. 添加音乐和音效
7. 添加转场效果
8. 调色（可选）
9. 导出
```

### 快捷键汇总
| 快捷键 | 功能 |
|--------|------|
| Ctrl+N | 新建项目 |
| Ctrl+I | 导入素材 |
| Ctrl+M | 智能字幕 |
| Ctrl+E | 智能抠像 |
| Ctrl+Z | 撤销 |
| Ctrl+Shift+Z | 重做 |
| Space | 播放/暂停 |
| +/- | 缩放时间轴 |

---

## 二、FFmpeg

### 安装
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows
# 下载exe或使用包管理器
```

### 基础命令

#### 1. 格式转换
```bash
# MP4转MOV
ffmpeg -i input.mp4 output.mov

# 转GIF
ffmpeg -i input.mp4 output.gif

# 提取音频
ffmpeg -i input.mp4 -vn -acodec copy output.mp3
```

#### 2. 视频处理
```bash
# 调整分辨率
ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4

# 调整帧率
ffmpeg -i input.mp4 -r 60 output.mp4

# 调整速度（2倍速）
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" output.mp4

# 裁剪视频
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:00:30 -c copy output.mp4
```

#### 3. 音视频合成
```bash
# 合并视频和音频
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4

# 添加背景音乐
ffmpeg -i video.mp4 -i music.mp3 -filter_complex amix=inputs=2:duration=first output.mp4
```

#### 4. 字幕处理
```bash
# 添加字幕
ffmpeg -i input.mp4 -vf subtitles=subtitle.srt output.mp4

# 烧录字幕
ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" -c:a copy output.mp4
```

### 批量处理脚本

#### 批量转换
```bash
#!/bin/bash
for f in *.mp4; do
    ffmpeg -i "$f" -c:v libx264 -c:a aac "${f%.mp4}_new.mp4"
done
```

#### 批量添加水印
```bash
#!/bin/bash
for f in *.mp4; do
    ffmpeg -i "$f" -i logo.png -filter_complex "overlay=10:10" "${f%.mp4}_watermarked.mp4"
done
```

---

## 三、Canva

### 快速开始
1. **访问**：canva.com
2. **注册**：免费账号
3. **创建**：选择视频模板

### 特点
- 拖拽式编辑
- 丰富的模板库
- 在线协作
- 导出为视频

### 适用场景
- 社交媒体视频
- 简单演示
- 快速出片

---

## 四、InVideo

### 快速开始
1. **访问**：invideo.io
2. **注册**：免费账号
3. **选择**：模板或空白项目

### 特点
- AI脚本生成
- 模板丰富
- 在线编辑
- 多平台导出

---

## 五、工具对比

| 工具 | 难度 | 功能 | 自动化 | 适合场景 |
|------|------|------|--------|----------|
| 剪映 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 专业剪辑 |
| FFmpeg | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 批量处理 |
| Canva | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 快速出片 |
| InVideo | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | AI辅助 |

---

## 六、推荐工作流

### 方案1：剪映为主
```
1. 剪映：导入素材，粗剪
2. 剪映：添加字幕、转场
3. 剪映：导出
4. FFmpeg：最终压缩/格式转换
```

### 方案2：FFmpeg自动化
```
1. 素材整理
2. FFmpeg脚本：批量处理
3. FFmpeg：合并音视频
4. FFmpeg：添加字幕
5. 导出
```

### 方案3：快速模板
```
1. Canva/InVideo：选择模板
2. 替换素材
3. 调整文字
4. 导出
```
