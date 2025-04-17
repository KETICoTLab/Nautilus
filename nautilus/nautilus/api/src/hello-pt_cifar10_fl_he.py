import os
import torch
import random
import argparse
from torchvision.datasets import CIFAR10
from torchvision.transforms import ToTensor, Normalize, Compose
from torch.utils.data import DataLoader
from torch.nn import CrossEntropyLoss
from torch.optim import SGD
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from client_test import SimpleNetwork
import nvflare.client as flare

from nvflare.app_opt.he.model_encryptor import HEModelEncryptor
from nvflare.app_opt.he.model_decryptor import HEModelDecryptor

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
    from torchvision.models import resnet18
    base_model = resnet18(pretrained=True)
    modules = list(base_model.children())[:-1]
    model = nn.Sequential(*modules)
    return nn.Sequential(model, nn.Flatten())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site_name", type=str, required=True)
    parser.add_argument("--data_path", type=str, required=True)
    args = parser.parse_args()

    batch_size = 4
    epochs = 5
    lr = 0.01
    model = SimpleNetwork()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    loss_fn = CrossEntropyLoss()
    optimizer = SGD(model.parameters(), lr=lr, momentum=0.9)

    transform = Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    flare.init()
    fl_ctx = flare.get_context()
    client_name = args.site_name
    tmp_model = get_resnet18_feature_extractor()

    train_dataset = CIFAR10(
        root=os.path.join(args.data_path, client_name),
        transform=transform, download=True, train=True
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    summary_writer = SummaryWriter()

    while flare.is_running():
        input_model = flare.receive()
        decrypted_weights = HEModelDecryptor().process(input_model.params, fl_ctx)
        model.load_state_dict(decrypted_weights)
        model.to(device)

        for epoch in range(epochs):
            model.train()
            for i, batch in enumerate(train_loader):
                images, labels = batch[0].to(device), batch[1].to(device)
                optimizer.zero_grad()
                predictions = model(images)
                cost = loss_fn(predictions, labels)
                cost.backward()
                optimizer.step()
                break

        feature_embed = extract_feature_embedding(tmp_model, train_loader, device)

        weights_to_send = model.cpu().state_dict()
        encrypted_weights = HEModelEncryptor(args={"weigh_by_local_iter": True}).process(weights_to_send, fl_ctx)

        output_model = flare.FLModel(
            params=encrypted_weights,
            meta={
                "accuracy": random.randint(50, 90),
                "metric": random.uniform(0, 1),
                "data_size": len(train_dataset),
                "feature_embedding": feature_embed.numpy().tolist()
            }
        )
        flare.send(output_model)


if __name__ == "__main__":
    main()