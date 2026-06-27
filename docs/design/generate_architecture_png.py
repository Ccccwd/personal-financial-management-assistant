# -*- coding: utf-8 -*-
"""生成 1920x1080 系统技术架构图 PNG（精简版）"""
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("请先安装: pip install pillow")

OUT = Path(__file__).parent / "系统技术架构图.png"
W, H = 1920, 1080


def load_fonts():
    paths = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]

    def font(size, bold=False):
        for p in paths:
            if not Path(p).exists():
                continue
            try:
                return ImageFont.truetype(p, size, index=1 if bold and p.endswith(".ttc") else 0)
            except Exception:
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    return font(40, True), font(20), font(22, True), font(18), font(16), font(15)


def rounded_rect(draw, box, radius, fill, outline, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=6)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = x0 + (x1 - x0 - tw) / 2
    y = y0 + (y1 - y0 - th) / 2
    draw.multiline_text((x, y), text, font=font, fill=fill, align="center", spacing=6)


def arrow_down(draw, x, y1, y2, color=(100, 116, 139), width=3):
    draw.line((x, y1, x, y2 - 12), fill=color, width=width)
    draw.polygon([(x, y2), (x - 8, y2 - 14), (x + 8, y2 - 14)], fill=color)


def arrow_right(draw, x1, y, x2, color=(100, 116, 139), width=3):
    draw.line((x1, y, x2 - 12, y), fill=color, width=width)
    draw.polygon([(x2, y), (x2 - 14, y - 8), (x2 - 14, y + 8)], fill=color)


def layer(draw, y, h, title, body, colors, fonts):
    f_layer, f_body = fonts
    x0, x1 = 200, 1720
    rounded_rect(draw, (x0, y, x1, y + h), 16, colors["bg"], colors["bd"], 2)
    draw.text((x0 + 28, y + 22), title, font=f_layer, fill=colors["title"])
    draw.text((x0 + 28, y + 58), body, font=f_body, fill=colors["body"])


def main():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    f_title, f_sub, f_layer, f_body, f_tag, f_deploy = load_fonts()

    draw.text((W // 2, 48), "智能个人财务记账系统 · 技术架构", font=f_title, fill=(15, 23, 42), anchor="mm")
    draw.text(
        (W // 2, 88),
        "前后端分离  |  RESTful API  |  JWT 认证  |  规则引擎 + DeepSeek",
        font=f_sub,
        fill=(100, 116, 139),
        anchor="mm",
    )

    # 五层架构（自上而下）
    layers = [
        (
            130,
            118,
            "用户层",
            "浏览器访问 Web 应用（PC / 移动端响应式）",
            {"bg": (255, 251, 235), "bd": (251, 191, 36), "title": (146, 64, 14), "body": (120, 53, 15)},
        ),
        (
            280,
            148,
            "表现层 · 前端",
            "Vue 3  +  TypeScript  +  Vite  +  Vue Router  +  Pinia  +  Element Plus  +  ECharts  +  Axios",
            {"bg": (237, 233, 254), "bd": (167, 139, 250), "title": (91, 33, 182), "body": (76, 29, 149)},
        ),
        (
            460,
            168,
            "应用层 · 后端 API",
            "FastAPI  +  Uvicorn  +  JWT 中间件  +  CORS / 限流  +  RESTful 路由  +  统一 JSON 响应",
            {"bg": (219, 234, 254), "bd": (96, 165, 250), "title": (30, 64, 175), "body": (29, 78, 216)},
        ),
        (
            660,
            148,
            "业务层 · 核心服务",
            "记账 / 账户 / 预算 / 统计  |  微信账单导入（自动分类）  |  AI 理财建议（DeepSeek）",
            {"bg": (209, 250, 229), "bd": (52, 211, 153), "title": (4, 120, 87), "body": (6, 95, 70)},
        ),
        (
            840,
            148,
            "数据层",
            "MySQL 8.0（9 张核心表，持久化存储）  |  Redis 7.x（缓存与健康检查）",
            {"bg": (255, 237, 213), "bd": (251, 146, 60), "title": (154, 52, 18), "body": (124, 45, 18)},
        ),
    ]

    for y, h, title, body, colors in layers:
        layer(draw, y, h, title, body, colors, (f_layer, f_body))

    # 层间箭头
    for y in (248, 428, 628, 808):
        arrow_down(draw, W // 2, y, y + 28)

    # 右侧外部服务
    rounded_rect(draw, (1380, 500, 1780, 720), 16, (254, 242, 242), (252, 165, 165), 2)
    center_text(
        draw,
        (1380, 500, 1780, 720),
        "外部服务\n\nDeepSeek API\ndeepseek-chat\n\nOpenAI SDK 兼容调用",
        f_layer,
        (185, 28, 28),
    )
    arrow_right(draw, 1280, 610, 1378, color=(239, 68, 68), width=3)
    draw.text((1305, 582), "LLM 调用", font=f_tag, fill=(185, 28, 28), anchor="mm")

    # 左侧通信标注
    draw.text((120, 368), "HTTPS\nREST\nJWT", font=f_tag, fill=(71, 85, 105), anchor="mm")
    arrow_right(draw, 168, 390, 198, width=2)

    # 底部部署
    rounded_rect(draw, (200, 1010, 1720, 1060), 12, (224, 231, 255), (165, 180, 252), 1)
    center_text(
        draw,
        (200, 1010, 1720, 1060),
        "部署：开发环境 Vite 代理 /api → FastAPI  |  生产环境 Vercel 前端 + Railway 后端",
        f_deploy,
        (55, 48, 163),
    )

    img.save(OUT, "PNG", optimize=True)
    print(f"已生成: {OUT}")


if __name__ == "__main__":
    main()
