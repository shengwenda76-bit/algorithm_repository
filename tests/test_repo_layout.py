"""本文件用于校验算法库平台脚手架目录是否已创建。"""

from pathlib import Path


def test_repo_layout_exists() -> None:
    """校验关键目录结构存在。"""

    assert Path("sdk/algorithm_sdk").is_dir()
    assert Path("algorithms").is_dir()
    assert Path("services/library_platform/registry").is_dir()
    assert Path("services/library_platform/catalog").is_dir()
    assert Path("services/library_platform/debug").is_dir()
    assert Path("tools").is_dir()
