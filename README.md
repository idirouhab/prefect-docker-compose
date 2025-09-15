# Prefect in Docker (Local UI + Worker + Your Flows)

This project runs [Prefect](https://prefect.io) entirely in Docker.  
You can edit Python flows locally, see them in the Prefect UI, and run them without building custom images.

---

## 🚀 Quick start

### 1. Start Prefect server + worker
```bat
docker compose up -d prefect-server worker
````

* UI available at: [http://localhost:4200](http://localhost:4200)
* Worker polls the `process-pool` for new runs

---

### 2. Create the work pool (one-time setup)

The worker needs a pool to poll. Run this once:

```bat
docker compose run --rm cli prefect work-pool create --type process process-pool
```

Confirm it exists:

```bat
docker compose run --rm cli prefect work-pool ls
```

Restart the worker so it connects:

```bat
docker compose up -d worker
```

---

### 3. Write a flow

Create `hello.py` in the project root:

```python
from prefect import flow, task, get_run_logger

@task
def say(msg: str):
    log = get_run_logger()
    log.info(msg)

@flow
def hello(name: str = "world"):
    say(f"👋 Hello, {name} from Prefect Process pool!")

if __name__ == "__main__":
    hello()
```

---

### 4. Register a deployment

Use the helper script `deploy.py` (included in this repo):

```python
# deploy.py
import sys
from prefect import flow

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py file.py:flow_func [file.py:flow_func ...]")
        sys.exit(1)

    for ep in sys.argv[1:]:
        print(f"→ Registering {ep}")
        f = flow.from_source(source="/app", entrypoint=ep)
        f.deploy(name=f"{f.name}-dev", work_pool_name="process-pool")
        print(f"✓ Created deployment '{f.name}/{f.name}-dev'")

if __name__ == "__main__":
    main()
```

Register your `hello` flow:

```bat
docker compose run --rm cli python deploy.py hello.py:hello
```

Check deployments:

```bat
docker compose run --rm cli prefect deployment ls
```

You should see `hello/hello-dev`.

---

### 5. Run the flow

#### On **Windows CMD** (no quotes):

```bat
docker compose run --rm cli prefect deployment run hello/hello-dev --watch
```

#### On **Windows PowerShell** (use double quotes):

```powershell
docker compose run --rm cli prefect deployment run "hello/hello-dev" --watch
```

Or trigger from the UI: **Deployments → hello / hello-dev → Run**.
Logs show up both in the UI and in the CLI.

---

## 📝 Adding new flows

1. Create a new file, e.g. `greet.py`:

   ```python
   from prefect import flow
   @flow
   def greet(who="Idir"):
       print(f"Hey {who}!")
   ```

2. Register it:

   ```bat
   docker compose run --rm cli python deploy.py greet.py:greet
   ```

3. Run it (same Windows rules apply):

    * CMD:

      ```bat
      docker compose run --rm cli prefect deployment run greet/greet-dev --watch
      ```
    * PowerShell:

      ```powershell
      docker compose run --rm cli prefect deployment run "greet/greet-dev" --watch
      ```

---

## 🛠 Useful commands

* View server logs:

  ```bat
  docker compose logs -f prefect-server
  ```

* View worker logs:

  ```bat
  docker compose logs -f worker
  ```

* List all deployments:

  ```bat
  docker compose run --rm cli prefect deployment ls
  ```

* List all work pools:

  ```bat
  docker compose run --rm cli prefect work-pool ls
  ```

* Tear everything down:

  ```bat
  docker compose down
  ```

---

## 📂 Project layout

```
.
├── docker-compose.yml   # Prefect server + worker + CLI
├── hello.py             # Example flow
├── deploy.py            # Deployment helper script
└── README.md            # This file
```

---

## ✅ Notes

* **No custom images**: your code is bind-mounted into the containers (`.:/app`).
* **Prefect UI**: [http://localhost:4200](http://localhost:4200).
* **Process pool**: runs flows directly on the worker container.
* Re-deploy flows if you **rename** them or add new ones.
  Small code edits are picked up automatically.