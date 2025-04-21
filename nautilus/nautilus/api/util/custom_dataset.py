# custom_dataset.py
import os
import random
from PIL import Image
from torch.utils.data import Dataset

class CustomCIFAR10Dataset(Dataset):
    def __init__(self, root_dir, transform=None, sample_size=500, mode='train', client_id=None, primary_ratio=0.9):
        self.root_dir = root_dir
        self.transform = transform
        self.sample_size = sample_size
        self.mode = mode
        self.primary_ratio = primary_ratio
        self.client_id = client_id
        self.images = []
        self.labels = []

        client_index = int(client_id.split("-")[1])
        feature_cycles = [[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 8], [8, 9, 0]] # [[9, 0, 1, 2, 3, 4], [2, 3, 4, 5, 6, 7], [5, 6, 7, 8, 9, 0]]
        primary_classes = feature_cycles[client_index % len(feature_cycles)]
        print(f"[CustomDataset] Primary classes for {client_id}: {primary_classes}")

        num_primary_classes = len(primary_classes)

        primary_sample_size = int(sample_size * primary_ratio) // num_primary_classes
        other_sample_size = (sample_size - primary_sample_size * num_primary_classes) // (10 - num_primary_classes)

        output_file = f"{mode}_{client_id}_sample_paths.txt"
        with open(output_file, 'w') as f:
            for primary_class in primary_classes:
                class_dir = os.path.join(root_dir, str(primary_class))
                if os.path.exists(class_dir):
                    images = os.listdir(class_dir)
 #                   print(f"[CustomDataset] Found {len(images)} images in primary class {primary_class}")
                    if len(images) >= primary_sample_size:
                        selected_images = random.sample(images, primary_sample_size)
                        self.images += [os.path.join(class_dir, img) for img in selected_images]
                        self.labels += [primary_class] * primary_sample_size
                        for img in selected_images:
                            f.write(f"{os.path.join(class_dir, img)}\n")

            for label in range(10):
                if label in primary_classes:
                    continue
                class_dir = os.path.join(root_dir, str(label))
                if os.path.exists(class_dir):
                    images = os.listdir(class_dir)
  #                  print(f"[CustomDataset] Found {len(images)} images in other class {label}")
                    if len(images) >= other_sample_size:
                        selected_images = random.sample(images, other_sample_size)
                        self.images += [os.path.join(class_dir, img) for img in selected_images]
                        self.labels += [label] * other_sample_size
                        for img in selected_images:
                            f.write(f"{os.path.join(class_dir, img)}\n")

        if len(self.images) == 0:
            raise ValueError(f"No images found in {root_dir}. Please check folder structure and image files.")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = self.images[idx]
        image = Image.open(image_path).convert("RGB")
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

                                   
