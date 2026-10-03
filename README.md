# Going Faster! 中文阅读版

一个可离线使用的静态 HTML 阅读器，包含 16 章正文及序言、附录、术语表等内容，配有 263 幅插图。

支持章节导航、全文搜索、字号调整、图片放大和阅读演示。正文采用 MiSans，默认字号 20px；图注随字号缩放。无需安装前端依赖或连接在线服务。


## 网站发布

在线阅读：<https://menttholatum.github.io/going-faster-cn/>。阅读页面、正文和图片对公众可见。

`.github/workflows/pages.yml` 在推送 `main` 或手动运行时构建、校验并部署网站。只有 `index.html`、阅读图片和字体目录进入网站发布包；源码数据、制作记录和单文件离线版不进入网站。

部署配置使用 **Settings → Pages → GitHub Actions**，仓库变量 `ENABLE_GITHUB_PAGES=true` 控制是否部署。删除该变量或将其设为 `false` 可暂停后续部署。实际发布状态以仓库 **Actions** 和 **Pages** 页面为准。

## 构建与校验

需要 Python 3.10 或更新版本，仅使用标准库：

```sh
python3 scripts/build.py
python3 scripts/validate-book.py --release
```

构建生成：

- `index.html`：日常阅读入口。
- `Going-Faster-全书中文阅读版.html`：字体和图片全部内嵌的单文件离线版。该文件较大，已加入 `.gitignore`，需要时本地生成。
- `output/`：构建信息和校验结果，已加入 `.gitignore`。

校验覆盖章节与页码完整性、图号、图片尺寸与哈希、页面锚点、字体许可，以及离线文件内嵌资源的一致性。构建不依赖原始 PDF、OCR 数据或机器上的绝对路径。

## 项目结构

```text
index.html                 阅读入口
content/book.json          正文、引语、编校注记和图注
content/figures.json        图片路径、尺寸和校验值
assets/figures/             阅读页使用的图片
assets/reader-fonts/        MiSans 字体及许可
scripts/                   阅读器模板、样式、交互和构建脚本
```

修改内容后运行构建命令。补充说明和阅读演示在界面中与正文区分，可通过工具栏隐藏。

## 版权与许可

《Going Faster!》的书中文字与图像版权归各自权利人所有；本项目不对这些内容授予开源许可。MiSans 按 `assets/reader-fonts/` 中保留的字体许可使用。

阅读器代码尚未指定开源许可证；仓库公开可见不构成对书本内容、图片的额外许可。字体许可不等同于书本内容的分发许可。
