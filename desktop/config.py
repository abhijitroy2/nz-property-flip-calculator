import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Dict, Any


APP_NAME = "RealFlip"


def _appdata_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _localdata_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


CONFIG_PATH = os.path.join(_appdata_dir(), "config.json")
LOG_DIR = os.path.join(_localdata_dir(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


ScheduleMode = Literal["interval", "cron"]


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""  # App password recommended
    recipients: List[str] = field(default_factory=list)


@dataclass
class ScheduleConfig:
    mode: ScheduleMode = "interval"
    minutes: int = 60  # for interval mode
    # for cron mode (any unset value is treated as wildcard)
    cron: Dict[str, Any] = field(default_factory=lambda: {
        "minute": "0",
        "hour": "0",
        "day": "*",
        "month": "*",
        "day_of_week": "*",
    })


@dataclass
class AppConfig:
    csv_paths: List[str] = field(default_factory=list)
    output_dir: str = os.path.join(os.path.expanduser("~"), "Documents", "RealFlipReports")
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    run_on_startup: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @staticmethod
    def from_json(s: str) -> "AppConfig":
        data = json.loads(s or "{}")
        email = EmailConfig(**data.get("email", {}))
        schedule = ScheduleConfig(**data.get("schedule", {}))
        return AppConfig(
            csv_paths=data.get("csv_paths", []),
            output_dir=data.get("output_dir", os.path.join(os.path.expanduser("~"), "Documents", "RealFlipReports")),
            schedule=schedule,
            email=email,
            run_on_startup=data.get("run_on_startup", False),
        )


def load_config() -> AppConfig:
    if not os.path.exists(CONFIG_PATH):
        cfg = AppConfig()
        save_config(cfg)
        return cfg
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return AppConfig.from_json(f.read())


def save_config(cfg: AppConfig) -> None:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(cfg.to_json())


