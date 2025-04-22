from util.job_tools_ssul import nt_Job_controller
from nvflare.job_config.script_runner import ScriptRunner
from src.simple_network import SimpleNetwork
import torch
import torchvision
from torchvision import transforms
from contrib.call_function import nt_contrib_evaluation
import argparse

def main():
    parser = argparse.ArgumentParser(description="Export FL Job with specified contribution method")
    parser.add_argument("--contribution_method", default="robust_volume", help="Method used to estimate client contribution")
    parser.add_argument("--server_url", default="172.17.0.1", help="Method used to post result")
    parser.add_argument("--n_clients", type=int, default=2, help="client num")
    parser.add_argument("--num_rounds", type=int, default=2, help="num round")
    parser.add_argument("--num_local_epoch", type=int, default=2, help="num local epoch")
    parser.add_argument("--job_name", default="hello-pt_cifar10_fedavg", help="job folder name")
    parser.add_argument("--project_id", default="p-kr-federated-learning-pj", help="project id")

    args = parser.parse_args()
    contribution_method = args.contribution_method
    n_clients = args.n_clients
    num_rounds = args.num_rounds
    num_local_epoch = args.num_local_epoch
    job_name = args.job_name
    project_id= args.project_id
    server_url = f"http://{args.server_url}:8000/nautilus/v1/projects/{project_id}/jobs/{job_name}/result/server"
    server_url_for_client = f"http://{args.server_url}:8000/nautilus/v1/projects/{project_id}/jobs/{job_name}/result/client"

    train_script = "src/hello-pt_cifar10_fl_ssul_featurecycle_eval.py"
    DATASET_PATH = "/tmp/nvflare/data"
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    batch_size = 256

    testset = torchvision.datasets.CIFAR10(root=DATASET_PATH, train=False, download=True, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)
    
        
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    # Client Selection Function is Now here
    
    job = nt_Job_controller(
        name=job_name, n_clients=n_clients, num_rounds=num_rounds, initial_model=SimpleNetwork(), contribution_method=contribution_method, server_url=server_url, project_id=project_id
    )

    # Add clients
    for i in range(n_clients):
        executor = ScriptRunner(
            script=train_script, script_args=f"--server_url {server_url_for_client} --num_local_epoch {num_local_epoch} --project_id {project_id}"  # f"--batch_size 32 --data_path /tmp/data/site-{i}"
        )
        job.to(executor, f"site-{i+1}")

    #job.export_job("/workspace/nautilus/nautilus/workspace/jobs")
    job.simulator_run("./test", gpu="0")
    
if __name__ == "__main__":
    main()
