# deploy.py
import sys, os, re, datetime as dt
from typing import Any, Dict
from prefect import flow
from prefect.client.schemas.schedules import CronSchedule, IntervalSchedule
import yaml

USAGE = "Usage: python deploy.py schedules.yaml"

_TIME_RE = re.compile(r"^\s*(\d+)\s*([smhd])\s*$", re.IGNORECASE)

def parse_every(s: str) -> dt.timedelta:
    m = _TIME_RE.match(s)
    if not m:
        raise ValueError(f"Invalid 'every': {s!r}. Use s/m/h/d, e.g. 15m, 2h.")
    val, unit = int(m.group(1)), m.group(2).lower()
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return dt.timedelta(seconds=val * mult)

def make_schedule(cfg: Dict[str, Any], fallback_tz: str):
    if not cfg:
        return None
    tz = cfg.get("timezone") or fallback_tz
    typ = (cfg.get("type") or "cron").lower()

    if typ == "cron":
        cron = cfg.get("cron")
        if not cron:
            raise ValueError("Missing 'cron' in schedule.")
        return CronSchedule(cron=cron, timezone=tz)

    if typ == "interval":
        every = cfg.get("every")
        if not every:
            raise ValueError("Missing 'every' in schedule (interval).")
        return IntervalSchedule(interval=parse_every(every), timezone=tz)

    raise ValueError(f"Unsupported schedule type: {typ!r}")

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(2)

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    defaults = data.get("defaults", {})
    default_pool = defaults.get("work_pool", "process-pool")
    default_tz = defaults.get("timezone", "UTC")

    flows = data.get("flows") or []
    if not flows:
        print("No 'flows' defined in YAML.")
        sys.exit(3)

    print(f"[deploy.py] Using work_pool={default_pool} timezone={default_tz}")
    for item in flows:
        entrypoint = item["entrypoint"]
        name = item["name"]
        params = item.get("parameters") or {}
        schedule_cfg = item.get("schedule")

        print(f"[deploy.py] → Registering {entrypoint} as '{name}'")
        pf_flow = flow.from_source(source="/app", entrypoint=entrypoint)

        schedule = make_schedule(schedule_cfg, default_tz) if schedule_cfg else None

        pf_flow.deploy(
            name=name,
            work_pool_name=default_pool,
            schedule=schedule,
            parameters=params if params else None,
        )
        print(f"[deploy.py] ✓ Deployment '{pf_flow.name}/{name}' created/updated")

    print("[deploy.py] Done.")

if __name__ == "__main__":
    main()
