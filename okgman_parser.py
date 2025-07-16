import ast
import os
import re
import json
import subprocess
import shutil
import hashlib
from install import download_package_folder, run_install_script_from_cache
from colorama import Fore, Style, init as colorama_init
from mkgen import build_mk
from tools import *

colorama_init(autoreset=True)
"""
global_build_info = {
    "project": {},
    "includes": [],
    "targets": [],
    "dependencies": [],
    "config": {},
    "shell_commands": [],
}

def project(name, version):
    global_build_info["project"] = {"name": name, "version": version}

def include(path):
    global_build_info["includes"].append(path)

def config(key, value):
    global_build_info["config"][key] = value

def exe(name, *sources,deps=None):
    global_build_info["targets"].append({
        "type": "executable",
        "name": name,
        "sources": list(sources),
        "flags": [],
        "deps": deps or []
    })

def lib(name, *sources):
    global_build_info["targets"].append({
        "type": "library",
        "name": name,
        "sources": list(sources),
        "flags": []
    })

def install(name, version=None):
    global_build_info["dependencies"].append({
        "name": name,
        "version": version,
    })

def shell(cmd):
    global_build_info["shell_commands"].append(cmd)
    print(f"[shell] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def files(pattern):
    return glob.glob(pattern)

def debug(enabled):
    config("DEBUG", enabled)
"""


# --- Hashing ---

def get_md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def has_pkgman_txt_changed(pkgman_path="pkgman.py", md5_path="build/pkgman.md5"):
    if not os.path.exists(pkgman_path):
        raise FileNotFoundError(f"{Fore.RED}[PANIC]{Style.RESET_ALL} {pkgman_path} not found.")

    current_md5 = get_md5(pkgman_path)

    if not os.path.exists(md5_path):
        return True

    with open(md5_path, "r") as f:
        stored_md5 = f.read().strip()

    return current_md5 != stored_md5

def save_pkgman_md5(pkgman_path="pkgman.txt", md5_path="build/pkgman.md5"):
    current_md5 = get_md5(pkgman_path)
    os.makedirs(os.path.dirname(md5_path), exist_ok=True)
    with open(md5_path, "w") as f:
        f.write(current_md5)


# --- Compiler & Build ---



def load_build_file(path="build/pkgman.build"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{Fore.RED}[PANIC]{Style.RESET_ALL} {path} not found.")
    with open(path, "r") as f:
        return json.load(f)

def compile_source(cc, src, obj, include_flags, extra_flags):
    os.makedirs(os.path.dirname(obj), exist_ok=True)
    cmd = [cc, "-c", src, "-o", obj] + include_flags + extra_flags
    print(f"{Fore.CYAN}[COMPILE]{Style.RESET_ALL} {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def get_dependencies(cc, src, include_flags, extra_flags):
    cmd = [cc, "-M"] + include_flags +extra_flags+ [src]
    output = subprocess.check_output(cmd, universal_newlines=True)
    # Çıktıyı temizle
    # "src/main.o: src/main.c include/header1.h include/header2.h"
    deps_line = output.strip().replace("\\", "")
    parts = deps_line.split(":")
    if len(parts) < 2:
        return []
    deps = parts[1].strip().split()
    return deps


def link_objects(cc, objs, out_path, extra_flags=None):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cmd = [cc] + objs + ["-o", out_path]
    if extra_flags:
        cmd += extra_flags
    print(f"{Fore.MAGENTA}[LINK]{Style.RESET_ALL} {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def install_dependencies(dependencies):
    for dep in dependencies:
        name = dep["name"]
        version = dep.get("version")
        print(f"{Fore.CYAN}[INSTALL]{Style.RESET_ALL} Installing {name} {version or ''}")
        folder = download_package_folder(name, version)
        run_install_script_from_cache(folder)
        shutil.rmtree(folder)
        print(f"{Fore.GREEN}[DONE]{Style.RESET_ALL} Installed {name}")


def load_hashes(path="build/file_hashes.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_hashes(hashes, path="build/file_hashes.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(hashes, f, indent=2)

def compile_if_needed(cc, src, obj, include_flags, extra_flags, file_hashes, updated_hashes):

    # Tüm bağımlılıkları al
    deps = get_dependencies(cc, src, include_flags, extra_flags)
    # Tüm bağımlılıkların hashlerini topla
    dep_hashes = {}
    for d in deps:
        if os.path.exists(d):
            dep_hashes[d] = get_md5(d)

    # Önceki hash karşılaştırması
    if all(file_hashes.get(d) == dep_hashes[d] for d in dep_hashes) and os.path.exists(obj):
        print(f"{Fore.BLUE}[SKIP]{Style.RESET_ALL} {src} and headers unchanged, skipping compilation.")
        # Hashleri güncelle
        updated_hashes.update(dep_hashes)
        return False
    else:
        # Derleme
        os.makedirs(os.path.dirname(obj), exist_ok=True)
        cmd = [cc, "-c", src, "-o", obj] + include_flags + extra_flags
        print(f"{Fore.CYAN}[COMPILE]{Style.RESET_ALL} {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        updated_hashes.update(dep_hashes)
        return True
"""
def run_pkgman_py(path="pkgman.py"):
    global global_build_info
    global_build_info = {
        "project": {},
        "includes": [],
        "targets": [],
        "dependencies": [],
        "config": {},
        "shell_commands": [],
    }

    # Python fonksiyonlarını da ekle
    env = {
        "project": project,
        "include": include,
        "config": config,
        "exe": exe,
        "lib": lib,
        "install": install,
        "shell": shell,
        "files": files,  # files fonksiyonunu glob ile tanımla
        "glob": glob,
        # gerekli diğer modüller ve fonksiyonlar...
    }

    with open(path, "r") as f:
        code = f.read()
    try:
        exec(code, env)
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to parse pkgman.py:\n{e}")
        raise
    return global_build_info
"""


"""
def build():
    pkgman_path = "pkgman.py"
    build_path = "build/pkgman.build"
    md5_path = "build/pkgman.md5"
    hashes_path = "build/file_hashes.json"

    # DSLParser ve dosya değişiklik kontrolü burada
    if has_pkgman_txt_changed(pkgman_path, md5_path) :
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} pkgman.txt changed, re-parsing...")
        build_info= run_pkgman_py(pkgman_path)
        os.makedirs(os.path.dirname(build_path), exist_ok=True)
        with open(build_path, "w") as f:
            json.dump(build_info, f, indent=2)
        save_pkgman_md5(pkgman_path, md5_path)
    else:
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} pkgman.txt unchanged, using cached build info.")

    build_info = load_build_file(build_path)
    includes = build_info.get("includes", [])
    config = build_info.get("config", {})
    project = build_info.get("project", {})
    project_name = project.get("name", "default")
    global_flags = config.get("CFLAGS", [])
    global_ldflags = config.get("LDFLAGS", [])
    cc = config.get("CC", find_cc())

    if config.get("DEBUG", False):
        global_flags += ["-g", "-O0"]
    else:
        global_flags += ["-O2"]

    if os.path.exists("vendor/include"):
        includes.append("vendor/include")

    include_flags = [f"-I{inc}" for inc in includes]

    file_hashes = load_hashes(hashes_path)
    updated_hashes = {}

    lib_names = []
    # Kütüphaneler derleniyor
    for target in build_info["targets"]:
        if target["type"] == "library":
            name = target["name"]
            lib_names.append(name)
            sources = target["sources"]
            flags = global_flags + target.get("flags", [])
            obj_files = []
            obj_dir = os.path.join("build", "obj", project_name, name)
            lib_dir = os.path.join("build", "lib")

            for src in sources:
                base = os.path.basename(src)
                obj = os.path.join(obj_dir, os.path.splitext(base)[0] + ".o")
                compile_if_needed(cc, src, obj, include_flags, flags, file_hashes, updated_hashes)
                obj_files.append(obj)

            os.makedirs(lib_dir, exist_ok=True)
            lib_path = os.path.join(lib_dir, f"lib{name}.a")
            cmd = ["ar", "rcs", lib_path] + obj_files
            print(f"{Fore.CYAN}[AR]{Style.RESET_ALL} {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Built library: {lib_path}")

    # Executable derleme
    for target in build_info["targets"]:
        if target["type"] != "executable":
            continue
        name = target["name"]
        sources = target["sources"]
        flags = global_flags + target.get("flags", [])
        obj_files = []
        obj_dir = os.path.join("build", "obj", project_name)

        for src in sources:
            base = os.path.basename(src)
            obj = os.path.join(obj_dir,os.path.splitext(base)[0] + ".o")
            compile_if_needed(cc, src, obj, include_flags, flags, file_hashes, updated_hashes)
            obj_files.append(obj)

        bin_path = os.path.join("build", name)
        lib_flags = [f"-Lbuild/lib"] + [f"-l{lib}" for lib in lib_names] + global_ldflags
        if os.path.exists("vendor/lib"):
            lib_flags.append("-Lvendor/lib")

        link_objects(cc, obj_files, bin_path, extra_flags=lib_flags)
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Built executable: {bin_path}")

        save_hashes(updated_hashes, hashes_path)
        return bin_path
"""

def build():
    build_mk("pkgman.py")

def clean():
    build_dir = "build"
    if os.path.exists(build_dir):
        print(f"{Fore.YELLOW}[CLEAN]{Style.RESET_ALL} Removing {build_dir}/")
        shutil.rmtree(build_dir)
        print(f"{Fore.GREEN}[DONE]{Style.RESET_ALL} Clean complete.")
    else:
        print(f"{Fore.BLUE}[SKIP]{Style.RESET_ALL} Nothing to clean.")
