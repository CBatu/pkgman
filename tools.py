import shutil
from colorama import Fore, Style


def find_cc():
    for cc in ["cc", "gcc", "clang"]:
        path = shutil.which(cc)
        if path:
            print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Compiler found: {cc}")
            return cc
    raise RuntimeError(f"{Fore.RED}[PANIC]{Style.RESET_ALL} No C compiler found.")

def find_ld():
    for ld in ["ld", "ld.lld", "lld-link"]:
        path = shutil.which(ld)
        if path:
            print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Linker found: {ld}")
            return ld
    raise RuntimeError(f"{Fore.RED}[PANIC]{Style.RESET_ALL} No linker found.")

def find_ar():
    for ar in ["ar", "llvm-ar"]:
        path = shutil.which(ar)
        if path:
            print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Archiver found: {ar}")
            return ar
    raise RuntimeError(f"{Fore.RED}[PANIC]{Style.RESET_ALL} No archiver found.")