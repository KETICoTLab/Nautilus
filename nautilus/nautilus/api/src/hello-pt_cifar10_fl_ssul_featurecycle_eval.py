import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))
from util.api_tools import http_post
from util.custom_iid_dataset import IIDCustomCIFAR10Dataset
import torch
from simple_network import SimpleNetwork
from torch import nn
from torch.optim import SGD
from torch.utils.data.dataloader import DataLoader
from torchvision.datasets import CIFAR10
from torchvision.transforms import Compose, Normalize, ToTensor
from torchvision.models import resnet18

import nvflare.client as flare
from nvflare.client.tracking import SummaryWriter
import random
import time

DATASET_PATH = "/tmp/nvflare/data/cifar10_custom_dataset"

def evaluate(model, testloader, device, loss_fn):
    model.to(device)
    model.eval()
    correct = 0
    total = 0
    total_loss = 0.0

    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = model(images)
            loss = loss_fn(outputs, labels)
            total_loss += loss.item() * labels.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct // total
    avg_loss = total_loss / total
    return accuracy, avg_loss


def extract_feature_embedding(model, dataloader, device, max_batches=10):
    model.to(device)
    model.eval()
    features = []
    with torch.no_grad():
        for i, (images, _) in enumerate(dataloader):
            if max_batches is not None and i >= max_batches:
                break
            images = images.to(device)
            x = model(images)
            features.append(x.view(x.size(0), -1).cpu())
    return torch.cat(features, dim=0)
def get_resnet18_feature_extractor():
    base_model = resnet18(pretrained=True)
    modules = list(base_model.children())[:-1]  # remove final FC
    model = nn.Sequential(*modules)
    return nn.Sequential(
        model,
        nn.Flatten()  # output shape: (batch, 512)
    )

def main(server_url: str, num_local_epoch: int, project_id: str):
    batch_size = 32
    epochs = num_local_epoch
    lr = 0.01
    model = SimpleNetwork()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    loss = nn.CrossEntropyLoss()
    optimizer = SGD(model.parameters(), lr=lr, momentum=0.9)

    transforms = Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    flare.init()
    sys_info = flare.system_info()
    client_name = sys_info["site_name"]
    tmp_model = get_resnet18_feature_extractor()

    train_dataset = IIDCustomCIFAR10Dataset(
        root_dir=os.path.join(DATASET_PATH, "train"),
        transform=transforms,
        mode="train",
        client_id=client_name,
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    test_dataset = IIDCustomCIFAR10Dataset(
        root_dir=os.path.join(DATASET_PATH, "test"),
        transform=transforms,
        mode="test",
        client_id=client_name,
    )
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"[{client_name}] TRAIN LABEL DISTRIBUTION:")
    print(Counter(train_dataset.labels))

    print(f"[{client_name}] TEST LABEL DISTRIBUTION:")
    print(Counter(test_dataset.labels))
    
    summary_writer = SummaryWriter()

    while flare.is_running():
        input_model = flare.receive()
        model.load_state_dict(input_model.params)
        model.to(device)

        for epoch in range(epochs):
            model.train()
            for i, batch in enumerate(train_loader):
                images, labels = batch[0].to(device), batch[1].to(device)
                optimizer.zero_grad()
                predictions = model(images)
                cost = loss(predictions, labels)
                cost.backward()
                optimizer.step()

            # evaluation 
            local_accuracy, local_loss = evaluate(model, test_loader, device, loss)
            payload = {
                "event_type": "client_result_created",
                "data": {
                    "project_id": project_id,
                    "client_name": client_name,
                    "epoch": epoch,
                    "local_accuracy": local_accuracy,
                    "local_loss": local_loss
                }
            }
            response = http_post(server_url, payload)

            print(f"\n[CLIENT]\nPOST > {server_url}\n payload > {payload}\n")
            if response:
                print(f"Results : {response}")
            else:
                print("else) Results")


        feature_embed = extract_feature_embedding(tmp_model, train_loader, device)  # shape (N, D)

        accuracy, loss_met = evaluate(model, test_loader, device, loss)
        #accuracy = random.randint(50, 90)
        #loss_met = random.uniform(0, 1)
        data_size = len(train_dataset)

        output_model = flare.FLModel(
            params=model.cpu().state_dict(),
            meta={
                "accuracy": accuracy,
                "metric": loss_met,
                "data_size": data_size,
                "feature_embedding": feature_embed.numpy().tolist()  # numpy array -> list
            },
        )
        flare.send(output_model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FL client with optional server_url")
    parser.add_argument("--server_url", type=str, required=True, help="Server URL to send results to")
    parser.add_argument("--num_local_epoch", type=int, default=2, help="num_local_epoch")
    parser.add_argument("--project_id", type=str, required=True, help="project_id")
    args = parser.parse_args()

    main(server_url=args.server_url, num_local_epoch=args.num_local_epoch, project_id=args.project_id)
