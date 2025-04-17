import os
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

DATASET_PATH = "/tmp/nvflare/data"

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

def main():
    batch_size = 4
    epochs = 5
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

    train_dataset = CIFAR10(
        root=os.path.join(DATASET_PATH, client_name), transform=transforms, download=True, train=True
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

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
                break

        feature_embed = extract_feature_embedding(tmp_model, train_loader, device)  # shape (N, D)

        accuracy = random.randint(50, 90)
        loss_met = random.uniform(0, 1)
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
    main()
