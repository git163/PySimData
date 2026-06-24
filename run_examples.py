#!/usr/bin/env python
"""自动运行 examples 目录下所有示例"""
import os
import sys
import subprocess

def main():
    examples_dir = "examples"

    if not os.path.exists(examples_dir):
        print(f"目录 {examples_dir} 不存在")
        return

    # 获取所有 .py 文件
    files = sorted(f for f in os.listdir(examples_dir) if f.endswith(".py"))

    if not files:
        print(f"目录 {examples_dir} 中没有 .py 文件")
        return

    print(f"找到 {len(files)} 个示例文件")
    print("=" * 50)

    for f in files:
        print(f"\n运行: {f}")
        print("-" * 30)
        result = subprocess.run(
            [sys.executable, f"{examples_dir}/{f}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # 打印最后几行输出
            lines = result.stdout.strip().split("\n")
            for line in lines[-3:]:
                print(line)
        else:
            print(f"错误: {result.stderr}")

    print("\n" + "=" * 50)
    print("完成!")


if __name__ == "__main__":
    main()