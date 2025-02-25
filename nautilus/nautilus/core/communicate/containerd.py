import subprocess

def is_image_exists(image_name: str) -> bool:
    """containerd에 특정 이미지가 존재하는지 확인"""
    try:
        result = subprocess.run(
            ["ctr", "images", "list", "-q"],
            capture_output=True, text=True, check=True
        )
        images = result.stdout.splitlines()
        return image_name in images
    except subprocess.CalledProcessError as e:
        print(f"❌ Containerd image retrieval failed: {e.stderr}")
        return False

def remove_containerd_image(image_name: str) -> bool:
    """containerd에서 특정 이미지 삭제"""
    if not is_image_exists(image_name):
        print(f"⚠️ '{image_name}' does not exist.")
        return False
    try:
        subprocess.run(["ctr", "images", "rm", image_name], check=True)
        print(f"🗑️ Image deletion complete: {image_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Image deletion failed: {e.stderr}")
        return False

def load_containerd_image(tar_path: str):
    """containerd에 tar 이미지 로드"""
    try:
        result = subprocess.run(["ctr", "images", "import", tar_path], capture_output=True, text=True, check=True)
        print(f"✅ Image load complete: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Image load Failed: {e.stderr}")
