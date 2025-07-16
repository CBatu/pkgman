# 📄 pkgman — Simple Python-Based Package Manager & Build System

**pkgman** is a minimal, command-line C/C++ project initializer, builder, and lightweight package installer written in Python. It automates basic project setup and compilation using a custom `build.py` system that generates a `Makefile`.

---

## ✨ Features

* 🔧 `init`: Start a new C project with a single command.
* 🏗️ `build`: Auto-generate a `Makefile` and compile using system tools (`cc`, `ar`, `ld`).
* 🧹 `clean`: Clean build artifacts.
* 🔁 `rebuild`: Clean and rebuild.
* 📦 `install`: Install packages from a package repository or local cache (WIP).
* 🧠 Modular and extensible Python-based CLI system (`arg.py`).

---

## 📅 Installation

### Option 1: Clone & Run

```bash
git clone https://github.com/CBatu/pkgman.git
cd pkgman
python3 pkgman.py --help
```

### Option 2: Install Globally (Dev Mode)

```bash
pip install -e .
```

Now you can use `pkgman` directly from anywhere:

```bash
pkgman build
```

### Option 3: Symlink (Unix systems)

```bash
chmod +x pkgman.py
sudo ln -s $(pwd)/pkgman.py /usr/local/bin/pkgman
```

---

## 💻 Usage

### Initialize a new C project

```bash
pkgman init --name hello
```

Creates:

```
hello/
├── build.py
└── main.c
```

---

### Build the project

```bash
pkgman build
```

Generates a `Makefile` and compiles the target.

---

### Clean build artifacts

```bash
pkgman clean
```

---

### Rebuild from scratch

```bash
pkgman rebuild
```

---

### Install a package (WIP)

```bash
pkgman install --name mylib --version 1.0 -f
```

---

## 💠 Example `build.py`

```python
from build_system import *

project("hello")
config("DEBUG", True)
exe("hello", "main.c")
```

This file is parsed by `pkgman` and translated into a `Makefile`.

---

## 🧪 Test Run Example

```bash
pkgman init --name hello
cd hello
# edit main.c
pkgman build
./build/hello
```

---

## 🣨 Convert to `.exe` (Windows Only)

Install PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile pkgman.py
```

Output will be in `dist/pkgman.exe`. You can now run `pkgman` anywhere on Windows.

---

## 📂 Project Structure

```
pkgman/
├── pkgman.py              # Main CLI entry
├── arg.py                 # Command parser
├── install.py             # Package install logic
├── build_system.py        # Build file to Makefile logic
├── init.py                # Project generator
├── okgman_parser.py       # Wrapper for build/clean
├── tools.py               # Detects compiler/linker
├── README.md
└── requirements.txt
```

---

## 🔮 Planned Features

* `search`, `update`, `uninstall` commands
* Dependency resolution system
* Binary package hosting
* Configurable registry (custom source URLs)

---

## 📜 License

MIT License. Use freely, modify openly.

---

> Made with ❤️ in Python.
