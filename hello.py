from prefect import flow, task, get_run_logger

@task
def say(msg: str):
    log = get_run_logger()
    log.info(msg)

@flow
def hello(name: str = "world"):
    say(f"👋 Hello, {name} from Prefect Process pool!")

if __name__ == "__main__":
    # Register a deployment that uses the local code (no image, no storage)
    hello.deploy(
        name="hello-dev",
        work_pool_name="process-pool",
        skip_upload=True,  # <-- key line
    )
