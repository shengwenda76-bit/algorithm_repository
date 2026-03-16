"""应用配置模块。"""

from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover - 当前环境未安装时使用降级实现
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        """在缺少 pydantic-settings 时兜底使用的配置基类。"""

    def SettingsConfigDict(**kwargs):
        """兼容 pydantic-settings API 的简化配置工厂。"""

        return kwargs


class Settings(BaseSettings):
    """集中管理运行时配置，后续可继续扩展。"""

    app_name: str = "algorithm-platform"
    app_env: str = "dev"
    debug: bool = True
    private_pypi_url: str = "https://pypi.internal.example/simple"
    package_cache_dir: Path = Path(".runtime/package_cache")

    model_config = SettingsConfigDict(
        env_prefix="ALGO_",
        extra="ignore",
    )


settings = Settings()
