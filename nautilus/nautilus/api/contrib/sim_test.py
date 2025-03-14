from util.job_tools import nt_Job_controller
from nvflare.job_config.script_runner import ScriptRunner
from client_test import SimpleNetwork

if __name__ == "__main__":
    n_clients = 2
    num_rounds = 2
    train_script = "client_contribution/src/hello-pt_cifar10_fl.py"

    # Client Selection Function is Now here
    
    job = nt_Job_controller(
        name="hello-pt_cifar10_fedavg", n_clients=n_clients, num_rounds=num_rounds, initial_model=SimpleNetwork()
    )

    # Add clients
    for i in range(n_clients):
        executor = ScriptRunner(
            script=train_script, script_args=""  # f"--batch_size 32 --data_path /tmp/data/site-{i}"
        )
        job.to(executor, f"site-{i}")

    # job.export_job("/tmp/nvflare/jobs/job_config")
    job.simulator_run("./test", gpu="0")