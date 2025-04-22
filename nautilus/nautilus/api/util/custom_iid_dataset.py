class IIDCustomCIFAR10Dataset(Dataset):
    def __init__(self, root_dir, transform=None, sample_size=5000, mode='train'):
        self.root_dir = root_dir
        self.transform = transform
        self.mode = mode
        self.sample_size = sample_size
        self.images = []
        self.labels = []

        # 전체 클래스 균등 샘플링
        classes = list(range(10))
        samples_per_class = sample_size // 10

        for cls in classes:
            class_dir = os.path.join(root_dir, str(cls))
            if not os.path.exists(class_dir):
                continue
            all_images = os.listdir(class_dir)
            selected_images = random.sample(all_images, samples_per_class)
            self.images += [os.path.join(class_dir, img) for img in selected_images]
            self.labels += [cls] * samples_per_class

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label
