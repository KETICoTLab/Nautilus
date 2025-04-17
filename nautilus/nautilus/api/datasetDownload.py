import os
import cv2
import numpy as np
import random
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.datasets import CIFAR10
from tqdm import tqdm

DATASET_DIR = "/tmp/nvflare/data/cifar10_custom_dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

def save_cifar10_images():

    # torchvision CIFAR10 �~M��~]��~D��~E~K �~\�~S~\
    trainset = CIFAR10(root='./data', train=True, download=True)
    testset = CIFAR10(root='./data', train=False, download=True)

    for dataset, split in [(trainset, "train"), (testset, "test")]:
        split_dir = os.path.join(DATASET_DIR, split)
        os.makedirs(split_dir, exist_ok=True)

        for idx, (img, label) in tqdm(enumerate(dataset), desc=f"Saving {split} images"):
            label_dir = os.path.join(split_dir, str(label))
            os.makedirs(label_dir, exist_ok=True)

            img_np = np.array(img)
            img_path = os.path.join(label_dir, f"{idx}.png")
            cv2.imwrite(img_path, cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))

save_cifar10_images()

