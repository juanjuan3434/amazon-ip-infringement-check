#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doctor.py — 环境自检：装完这个技能后先跑一次，确认本机能不能正常用。

用法：
    python doctor.py

只做检查，不改动任何文件、不联网。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

OK = "[ OK ]"
WARN = "[WARN]"
FAIL = "[FAIL]"

results = []


def add(level, title, detail=""):
    results.append((level, title, detail))


def check_python():
    v = sys.version_info
    if v >= (3, 9):
        add(OK, f"Python {v.major}.{v.minor}.{v.micro}", sys.executable)
    else:
        add(FAIL, f"Python {v.major}.{v.minor} 版本过低", "需要 3.9+，请升级 Python")


def check_optional_module(mod, why):
    try:
        __import__(mod)
        add(OK, f"可选依赖 {mod}", "已安装")
    except ImportError:
        add(WARN, f"可选依赖 {mod} 未安装", f"仅在用到时才会报错 —— {why}；安装：python -m pip install {mod}")


def check_node():
    exe = shutil.which("node")
    if not exe:
        add(WARN, "未找到 Node.js", "`.js` 脚本（amz.js / dl*.js / fetch*.js）不可用；抓 Amazon/站点页时会用到")
        return
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=15)
        ver = out.stdout.strip()
        major = int(ver.lstrip("v").split(".")[0]) if ver.startswith("v") else 0
        if major >= 18:
            add(OK, f"Node.js {ver}", exe + "（内置 fetch 可用）")
        else:
            add(WARN, f"Node.js {ver} 版本偏低", "建议 18+，否则 fetch 相关脚本不可用")
    except Exception as exc:  # noqa: BLE001
        add(WARN, "Node.js 版本检测失败", str(exc))


def check_scripts():
    expected = [
        "g4.py", "sheets.py", "decode.py", "catalog.py", "batch.py", "extract.py",
        "zoom.py", "fmt.py", "h2t.py", "pfpo.py", "ctx.py", "detail.py", "x2.py",
        "ximgs.py", "uimgs.py", "relimgs.py", "relimgs2.py", "prodimg.py",
        "evidence.py", "cmpside.py", "mapimg.py", "decf.py", "decf2.py", "pdftext.py",
        "amz.js", "dl.js", "dl_list.js", "dl_list2.js", "dl_ep.js", "fetch_site.js",
        "fetchall.js",
    ]
    missing = [f for f in expected if not os.path.exists(os.path.join(HERE, f))]
    if missing:
        add(FAIL, f"脚本缺失 {len(missing)} 个", ", ".join(missing) + "（下载不完整？）")
    else:
        add(OK, f"脚本齐全（{len(expected)} 个）", HERE)


def check_decoder():
    """最重要的自检：g4 解码器能否从脚本自身目录加载（历史 bug 点）。"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("g4", os.path.join(HERE, "g4.py"))
        g4 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(g4)
        need = ["decode_g4", "write_png_gray"]
        lack = [n for n in need if not hasattr(g4, n)]
        if lack:
            add(FAIL, "g4.py 加载成功但缺少函数", ", ".join(lack))
        else:
            add(OK, "g4 解码器可加载", "decode_g4 / write_png_gray 均存在")
    except Exception as exc:  # noqa: BLE001
        add(FAIL, "g4 解码器加载失败", f"{type(exc).__name__}: {exc}")


def check_workdir():
    wd = os.environ.get("IPCHECK_DIR") or os.getcwd()
    if not os.path.isdir(wd):
        add(FAIL, "工作目录不存在", wd)
        return
    probe = os.path.join(wd, "_wb_write_probe.tmp")
    try:
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(probe)
        src = "IPCHECK_DIR 环境变量" if os.environ.get("IPCHECK_DIR") else "当前目录"
        add(OK, "工作目录可写", f"{wd}（来自{src}）")
    except Exception as exc:  # noqa: BLE001
        add(FAIL, "工作目录不可写", f"{wd} → {exc}")


def main():
    print("=" * 62)
    print(" amazon-ip-infringement-check 环境自检")
    print("=" * 62)
    check_python()
    check_scripts()
    check_decoder()
    check_workdir()
    check_node()
    check_optional_module("PIL", "cmpside.py / decf*.py / relimgs*.py / prodimg.py 拼图")
    check_optional_module("pypdf", "pdftext.py 抽专利 PDF 文本与权利要求")

    fails = warms = 0
    for level, title, detail in results:
        if level == FAIL:
            fails += 1
        elif level == WARN:
            warms += 1
        print(f"{level} {title}")
        if detail:
            print(f"       {detail}")

    print("-" * 62)
    if fails == 0:
        print(f"结论：核心功能可用 ✅   警告 {warms} 条（不影响主流程）")
        print()
        print("下一步：cd 进你的案例目录（放 PDF / 图片的地方），然后例如：")
        print(f'  python "{os.path.join(HERE, "sheets.py")}" D1000009 2,3')
        return 0
    print(f"结论：有 {fails} 项必须修复 ❌（见上面 FAIL 行），警告 {warms} 条")
    return 1


if __name__ == "__main__":
    sys.exit(main())
