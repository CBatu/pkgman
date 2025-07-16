import os
import glob
import sys
from tools import *

# --- Global Build Context ---
build_context = {
    "project": {"name": "default", "version": ""},
    "config": {},           # CFLAGS, LDFLAGS, CC, DEBUG vb
    "includes": [],         # include pathleri
    "targets": [],          # exe, lib gibi hedefler
    "functions": {},        # fonksiyon isim -> shell komutu
    "custom_steps": [],     # farklı türde özel build adımları (tuple (type, dict))
    "variables": {},        # ek değişkenler
}

def files(pattern):
    return glob.glob(pattern)

# --- API Fonksiyonları ---

def project(name, version=""):
    build_context["project"] = {"name": name, "version": version}

def config(key, value):
    build_context["config"][key] = value

def include(path):
    build_context["includes"].append(path)

def shell(cmd, name=None, deps=None):
    if name is None:
        build_context["custom_steps"].append(("shell", {"cmd": cmd, "deps": deps or []}))
    else:
        build_context["functions"][name] = {
            "cmd": cmd,
            "deps": deps or [],
        }

def exe(name, *sources, deps=[]):
    build_context["targets"].append({
        "type": "executable",
        "name": name,
        "sources": list(sources),
        "deps": deps,
    })

def lib(name, *sources, deps=[]):
    build_context["targets"].append({
        "type": "library",
        "name": name,
        "sources": list(sources),
        "deps": deps,
    })

def custom_step(step_type, **kwargs):
    build_context["custom_steps"].append((step_type, kwargs))

def variable(name, value):
    build_context["variables"][name] = value

# --- Makefile üreticisi ---

def generate_makefile(out_path="Makefile"):
    p = build_context["project"]
    proj_name = p.get("name", "default")
    includes = build_context["includes"]
    config = build_context["config"]
    targets = build_context["targets"]
    functions = build_context["functions"]
    custom_steps = build_context["custom_steps"]
    variables = build_context["variables"]

    cc = config.get("CC", find_cc())
    ar = config.get("AR", find_ar())
    ld = config.get("LD", find_cc())

    cflags = config.get("CFLAGS", [])
    ldflags = config.get("LDFLAGS", [])
    debug = config.get("DEBUG", False)

    debug_flags = ["-g", "-O0"] if debug else ["-O2"]
    include_flags = [f"-I{inc}" for inc in includes]

    lines = []
    lines.append("SHELL := /bin/bash")
    lines.append(f"CC = {cc}")
    lines.append(f"AR = {ar}")
    lines.append(f"LD = {ld}")
    lines.append(f"CFLAGS = {' '.join(debug_flags + ['-MMD', '-MP'] + cflags + include_flags)}")
    lines.append(f"LDFLAGS = {' '.join(ldflags)}")

    for var, val in variables.items():
        if isinstance(val, (list, tuple)):
            val = " ".join(val)
        lines.append(f"{var} = {val}")

    lines.append("")
    lines.append(".PHONY: all clean " + " ".join(functions.keys()))
    lines.append("")

    all_bins = []
    lib_targets = []

    # Fonksiyon hedefleri
    for fname, info in functions.items():
        cmd = info["cmd"]
        deps = info.get("deps", [])
        dep_str = " ".join(deps)
        lines.append(f"{fname}: {dep_str}")
        lines.append(f'\t@echo -e "\\033[1;37m[SHELL]\\033[0m Running {fname} step"')
        lines.append(f"\t@{cmd}")
        lines.append("")

    # Kütüphane hedefleri
    for target in targets:
        if target["type"] != "library":
            continue

        libname = target["name"]
        libfile = f"build/lib/lib{libname}.a"
        lib_targets.append(libfile)
        obj_files = []

        for src in target["sources"]:
            base = os.path.splitext(os.path.basename(src))[0]
            obj_path = f"build/obj/{proj_name}/{libname}/{base}.o"
            obj_dir = os.path.dirname(obj_path)
            obj_files.append(obj_path)

            deps_makefile = [d if isinstance(d, str) else d.__name__ for d in target.get("deps", [])]
            dep_str = " ".join(deps_makefile)

            lines.append(f"{obj_path}: {src} {dep_str}")
            lines.append(f"\t@mkdir -p {obj_dir}")
            lines.append(f'\t@echo -e "\\033[1;36m[CC]\\033[0m Compiling {src}"')
            lines.append(f"\t@$(CC) $(CFLAGS) -c {src} -o {obj_path}")
            lines.append("")

        lines.append(f"{libfile}: {' '.join(obj_files)}")
        lines.append(f"\t@mkdir -p build/lib")
        lines.append(f'\t@echo -e "\\033[1;35m[AR]\\033[0m Archiving {libfile}"')
        lines.append(f"\t@$(AR) rcs {libfile} {' '.join(obj_files)}")
        lines.append("")

    # Executable hedefleri
    for target in targets:
        if target["type"] != "executable":
            continue

        name = target["name"]
        bin_path = f"build/{name}"
        bin_dir = os.path.dirname(bin_path)
        obj_files = []

        for src in target["sources"]:
            base = os.path.splitext(os.path.basename(src))[0]
            obj_path = f"build/obj/{proj_name}/{base}.o"
            obj_dir = os.path.dirname(obj_path)
            obj_files.append(obj_path)

            deps_makefile = [d if isinstance(d, str) else d.__name__ for d in target.get("deps", [])]
            dep_str = " ".join(deps_makefile)

            lines.append(f"{obj_path}: {src} {dep_str}")
            lines.append(f"\t@mkdir -p {obj_dir}")
            lines.append(f'\t@echo -e "\\033[1;36m[CC]\\033[0m Compiling {src}"')
            lines.append(f"\t@$(CC) $(CFLAGS) -c {src} -o {obj_path}")
            lines.append("")

        lib_links = " ".join([f"-l{lib['name']}" for lib in targets if lib["type"] == "library"])
        vendor_lib = "-Lvendor/lib" if os.path.exists("vendor/lib") else ""
        lib_links += "-Lbuild/lib" if os.path.exists("build/lib") else ""

        lines.append(f"{bin_path}: {' '.join(obj_files)} {' '.join(lib_targets)}")
        lines.append(f"\t@mkdir -p {bin_dir}")
        lines.append(f'\t@echo -e "\\033[1;33m[LD]\\033[0m Linking {bin_path}"')
        lines.append(f"\t@$(LD) {vendor_lib} {lib_links} {' '.join(obj_files)} -o {bin_path} $(LDFLAGS)")
        lines.append("")

        all_bins.append(bin_path)

    lines.insert(0, f"all: {' '.join(all_bins)}\n")

    # Özel adımlar
    for idx, (step_type, params) in enumerate(custom_steps):
        if step_type == "shell":
            name = f"custom_shell_{idx}"
            cmd = params.get("cmd", "echo Running shell step")
            lines.append(f".PHONY: {name}")
            lines.append(f"{name}:")
            lines.append(f'\t@echo -e "\\033[1;37m[SHELL]\\033[0m Running custom shell step"')
            lines.append(f"\t@{cmd}")
            lines.append("")
        elif step_type == "copy":
            src = params.get("src")
            dest = params.get("dest")
            if src and dest:
                name = f"copy_{idx}"
                lines.append(f".PHONY: {name}")
                lines.append(f"{name}:")
                lines.append(f'\t@echo -e "\\033[1;32m[COPY]\\033[0m Copying {src} -> {dest}"')
                lines.append(f"\tcp {src} {dest}")
                lines.append("")

    # clean hedefi
    lines.append("clean:")
    lines.append(f'\t@echo -e "\\033[1;31m[CLEAN]\\033[0m Removing build directory"')
    lines.append("\t@rm -rf build")
    lines.append("")

    help_lines = [
        "help:",
        '\t@echo -e "\\033[1;34mAvailable targets:\\033[0m"',
        '\t@echo -e "\\033[1;36m  all       \\033[0m - Build all executables"',
        '\t@echo -e "\\033[1;31m  clean     \\033[0m - Remove build directory"',
    ]

    for fname in functions:
        help_lines.append(f'\t@echo -e "\\033[1;37m  {fname:<10}\\033[0m - Custom shell command"')

    for idx, (step_type, _) in enumerate(custom_steps):
        name = f"{step_type}_{idx}"
        help_lines.append(f'\t@echo -e "\\033[1;37m  {name:<10}\\033[0m - Custom {step_type} step"')

    for target in targets:
        if target["type"] == "executable":
            help_lines.append(f'\t@echo -e "\\033[1;33m  build/{target["name"]:<10}\\033[0m - Executable target"')
        elif target["type"] == "library":
            help_lines.append(f'\t@echo -e "\\033[1;35m  lib{target["name"]}.a\\033[0m - Static library target"')

    lines.append("\n".join(help_lines))
    lines.append("-include build/obj/*.d")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Makefile generated at {out_path}")

# --- Kullanım girişi ---

def build_mk(build_config_file):
    if not os.path.exists(build_config_file):
        print(f"Hata: Yapılandırma dosyası bulunamadı: {build_config_file}", file=sys.stderr)
        exit(1)

    try:
        with open(build_config_file, "r") as f:
            config_code = f.read()

        exec(config_code)
        generate_makefile()

    except Exception as e:
        print(f"Yapılandırma dosyasını işlerken hata oluştu: {e}", file=sys.stderr)
        sys.exit(1)
