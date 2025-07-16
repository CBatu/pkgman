import os

def run_init_command(args):
    # Proje adı verilmemişse, bulunduğun klasör adı varsayılacak
    project_name = args.get("name")
    if not project_name:
        project_name = os.path.basename(os.getcwd())

    base_dir = os.getcwd()

    print(f"[INFO] Initializing C project in: {base_dir}")

    # 1. Klasör yapısı
    os.makedirs("src", exist_ok=True)
    os.makedirs("include", exist_ok=True)
    os.makedirs("build", exist_ok=True)

    # 2. Ana dosya: src/main.c
    main_c_path = os.path.join("src", "main.c")
    if not os.path.exists(main_c_path):
        with open(main_c_path, "w") as f:
            f.write(
                '#include <stdio.h>\n\n'
                'int main() {\n'
                '    printf("Hello from C project!\\n");\n'
                '    return 0;\n'
                '}\n'
            )

    # 3. Metadata: pkgman.txt
    with open("pkgman.py", "w") as f:
        f.write(f"project={project_name}\n")
        f.write("language=c\n")

    print(f"[SUCCESS] Project '{project_name}' initialized.")

def parse_pkgman_file(path="pkgman.txt"):
    if not os.path.exists(path):
        raise FileNotFoundError("[ERROR] pkgman.txt not found.")

    data = {}
    with open(path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                data[key.strip()] = value.strip()
    return data
