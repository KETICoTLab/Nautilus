from util.job_tools import nt_Job_controller
from nvflare.job_config.script_runner import ScriptRunner
from client_test import SimpleNetwork
import torch
import torchvision
from torchvision import transforms
from contrib.call_function import nt_contrib_evaluation

if __name__ == "__main__":
    n_clients = 2
    num_rounds = 2
    train_script = "src/hello-pt_cifar10_fl.py"
    DATASET_PATH = "/tmp/nvflare/data"
    
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    batch_size = 256

    testset = torchvision.datasets.CIFAR10(root=DATASET_PATH, train=False, download=True, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)
    
        
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
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
