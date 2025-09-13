# deploy.py
import sys
from prefect import flow

USAGE = """\
Usage:
  python deploy.py <file.py:flow_func> [<file.py:flow_func> ...]
Examples:
  python deploy.py hello.py:hello
  python deploy.py hello.py:hello greet.py:greet
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    for ep in sys.argv[1:]:
        if ":" not in ep:
            print(f"Invalid entrypoint '{ep}'. Expected format file.py:flow_func")
            sys.exit(2)

        print(f"→ Registering deployment for {ep}")
        f = flow.from_source(source="/app", entrypoint=ep)
        # No images, no storage; code runs from your bind mount
        f.deploy(name=f"{f.name}-dev", work_pool_name="process-pool")
        print(f"✓ Created deployment '{f.name}/{f.name}-dev'")

if __name__ == "__main__":
    main()
