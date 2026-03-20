"""本文件用于提供算法发布登记脚本的占位入口。"""


def build_register_payload(code: str, version: str, sha256: str) -> dict:
    """构造注册中心调用载荷。"""

    return {
        "code": code,
        "version": version,
        "artifact": {"sha256": sha256},
    }
