import os
import platform
import requests
import json
import subprocess
import shutil

# ----------------------------------------
# Platform Algılama
# ----------------------------------------

def detect_platform():
    sys = platform.system().lower()
    return {
        "darwin": "macos",
        "linux": "linux",
        "windows": "windows"
    }.get(sys, "unknown")

# ----------------------------------------
# package.json'dan paket klasörü bilgisi alma
# ----------------------------------------

def get_package_info(package_name, version, repo_user, repo_name, branch="main"):
    raw_url = f"https://raw.githubusercontent.com/{repo_user}/{repo_name}/{branch}/package.json"
    print(f"[INFO] Fetching package index from {raw_url}")
    
    response = requests.get(raw_url)
    response.raise_for_status()

    metadata = json.loads(response.text)
    packages = metadata.get("packages", {})
    
    if package_name not in packages:
        raise Exception(f"[ERROR] Package '{package_name}' not found.")

    versions = packages[package_name]
    if version not in versions:
        raise Exception(f"[ERROR] Version '{version}' not found for package '{package_name}'.")

    platform_key = detect_platform()
    folder = versions[version].get(platform_key)

    if not folder:
        raise Exception(f"[ERROR] Platform '{platform_key}' not supported for '{package_name} {version}'.")

    return folder

# ----------------------------------------
# GitHub API ile klasördeki tüm dosyaları listele (recursive)
# ----------------------------------------

def list_folder_files_from_github(user, repo, branch, folder_path):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{folder_path}?ref={branch}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    items = response.json()
    
    file_paths = []
    for item in items:
        if item["type"] == "file":
            file_paths.append(item["path"])
        elif item["type"] == "dir":
            # Recursive klasör tarama
            file_paths.extend(list_folder_files_from_github(user, repo, branch, item["path"]))
    
    return file_paths

# ----------------------------------------
# Tek bir dosyayı indir ve .cache içine kaydet
# ----------------------------------------

def download_file_from_repo(user, repo, branch, file_path, save_root=".cache"):
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
    local_path = os.path.join(save_root, file_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    print(f"[↓] {file_path}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(f"[ERROR] Failed to download {file_path}: HTTP {response.status_code}")

    return local_path

# ----------------------------------------
# Paketi klasör olarak indir
# ----------------------------------------

def download_package_folder(package_name, version, user="CBatu", repo="pkgman", branch="main"):
    folder = get_package_info(package_name, version, user, repo, branch)
    
    print(f"[INFO] Listing files in: {folder}")
    files = list_folder_files_from_github(user, repo, branch, folder)
    
    for file_path in files:
        download_file_from_repo(user, repo, branch, file_path)
    
    print(f"[SUCCESS] Downloaded all files to .cache/{folder}")
    return os.path.join(".cache", folder)

# ----------------------------------------
# install.sh çalıştır
# ----------------------------------------

def run_install_script_from_cache(folder_path):
    install_path = os.path.join(folder_path, "install.sh")
    if not os.path.exists(install_path):
        raise Exception("[ERROR] install.sh not found.")
    
    print(f"[RUN] Running install script: {install_path}")
    subprocess.run(["chmod", "+x", install_path])
    subprocess.run([install_path])
    print(f"[DONE] install.sh executed successfully.")