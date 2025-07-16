from sys import argv, exit
from colorama import Fore, Style, init

init(autoreset=True)

class Arg:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.args = argv
        self.commands = []

    def panic(self, message):
        print(f"{Fore.RED}[!] {message}{Style.RESET_ALL}")
        exit(1)

    def add_command(self, command, desc=None, func=None, aliases=None, args_spec=None):
        """
        args_spec: dict of argument specs like:
        {
            "name": {"type": str, "required": True, "desc": "Package name"},
            "version": {"type": str, "required": False, "default": "latest", "desc": "Package version"},
            "force": {"type": bool, "required": False, "alias": ["-f"], "desc": "Force install"}
        }
        """
        self.commands.append({
            "command": command,
            "desc": desc or "",
            "func": func,
            "aliases": aliases or [],
            "args_spec": args_spec or {}
        })

    def get_command(self, name):
        for c in self.commands:
            if c["command"] == name or name in c.get("aliases", []):
                return c
        return None

    def help(self, command=None):
        if command is None:
            # Genel yardım
            print(f"{Fore.CYAN}{self.name} - {self.desc}{Style.RESET_ALL}\n")
            print("Usage:")
            print(f"  python main.py {Fore.YELLOW}[command] [arguments]{Style.RESET_ALL}\n")
            print("Available commands:")
            for c in self.commands:
                aliases = ", ".join(c.get("aliases", []))
                alias_str = f" ({aliases})" if aliases else ""
                print(f"  {Fore.GREEN}{c['command']}{Style.RESET_ALL}{alias_str} - {c['desc']}")
            print()
        else:
            # Komut bazında yardım
            print(f"{Fore.CYAN}Help for command '{command['command']}'{Style.RESET_ALL}\n")
            print(f"{command['desc']}\n")
            print("Arguments:")
            for arg, spec in command.get("args_spec", {}).items():
                req = "Required" if spec.get("required") else "Optional"
                default = spec.get("default")
                alias = ", ".join(spec.get("alias", [])) if spec.get("alias") else ""
                aliases_str = f" Aliases: {alias}" if alias else ""
                default_str = f" Default: {default}" if default is not None else ""
                print(f"  {Fore.GREEN}{arg}{Style.RESET_ALL} ({spec.get('type', str).__name__}) - {req}{default_str}{aliases_str}")
                if spec.get("desc"):
                    print(f"      {spec['desc']}")
            print()

    def parse_args(self, raw_args, args_spec):
        """
        Parse raw args into flags, kv, positional based on args_spec.

        Returns dict of all args with values, applying defaults.
        """
        result = {}
        # map alias to arg name for quick lookup
        alias_map = {}
        for arg_name, spec in args_spec.items():
            for a in spec.get("alias", []):
                alias_map[a] = arg_name
        # Initialize defaults
        for arg_name, spec in args_spec.items():
            if "default" in spec:
                result[arg_name] = spec["default"]

        flags = set()
        positional = []
        i = 0
        while i < len(raw_args):
            arg = raw_args[i]
            if arg in ("--help", "-h"):
                i += 1
                continue

            # --flag or --key=value
            if arg.startswith("--"):
                if "=" in arg:
                    key, val = arg[2:].split("=", 1)
                    if key in args_spec:
                        result[key] = self.cast_type(val, args_spec[key].get("type", str))
                    else:
                        self.panic(f"Unknown argument: --{key}")
                else:
                    # flag or boolean arg
                    key = arg
                    if key in alias_map:
                        arg_name = alias_map[key]
                        spec = args_spec[arg_name]
                        if spec.get("type", bool) == bool:
                            result[arg_name] = True
                        else:
                            # expects a value next
                            if i + 1 >= len(raw_args):
                                self.panic(f"Expected value after {arg}")
                            i += 1
                            val = raw_args[i]
                            result[arg_name] = self.cast_type(val, spec.get("type", str))
                    else:
                        # no alias found, check direct name
                        key2 = arg[2:]
                        if key2 in args_spec:
                            spec = args_spec[key2]
                            if spec.get("type", bool) == bool:
                                result[key2] = True
                            else:
                                if i + 1 >= len(raw_args):
                                    self.panic(f"Expected value after {arg}")
                                i += 1
                                val = raw_args[i]
                                result[key2] = self.cast_type(val, spec.get("type", str))
                        else:
                            self.panic(f"Unknown argument: {arg}")

            elif arg.startswith("-") and len(arg) > 1:
                # short alias e.g. -f
                if arg in alias_map:
                    arg_name = alias_map[arg]
                    spec = args_spec[arg_name]
                    if spec.get("type", bool) == bool:
                        result[arg_name] = True
                    else:
                        if i + 1 >= len(raw_args):
                            self.panic(f"Expected value after {arg}")
                        i += 1
                        val = raw_args[i]
                        result[arg_name] = self.cast_type(val, spec.get("type", str))
                else:
                    self.panic(f"Unknown short argument: {arg}")
            elif "=" in arg:
                key, val = arg.split("=", 1)
                if key in args_spec:
                    result[key] = self.cast_type(val, args_spec[key].get("type", str))
                else:
                    self.panic(f"Unknown argument: {key}")
            else:
                # Positional
                positional.append(arg)
            i += 1

        # Positional to unnamed args? (optional: map if args_spec has positional order)

        # Validate required
        for arg_name, spec in args_spec.items():
            if spec.get("required") and arg_name not in result:
                self.panic(f"Missing required argument: {arg_name}")

        # Attach positional if needed
        result["_positional"] = positional

        return result

    def cast_type(self, val, t):
        try:
            if t == bool:
                # Support true/false strings
                if isinstance(val, str):
                    if val.lower() in ("true", "1", "yes"):
                        return True
                    elif val.lower() in ("false", "0", "no"):
                        return False
                    else:
                        raise ValueError(f"Cannot convert '{val}' to bool")
                return bool(val)
            return t(val)
        except Exception as e:
            self.panic(f"Failed to cast '{val}' to {t.__name__}: {e}")

    def parse(self):
        # Global help
        if "--help" in self.args or "-h" in self.args or len(self.args) == 1:
            self.help()
            exit(0)

        if len(self.args) < 2:
            self.help()
            self.panic("No command provided.")

        command_name = self.args[1]
        selected_command = self.get_command(command_name)
        if selected_command is None:
            self.help()
            self.panic(f"Unknown command: '{command_name}'")

        raw_args = self.args[2:]

        # Command-specific help
        if "--help" in raw_args or "-h" in raw_args:
            self.help(selected_command)
            exit(0)

        args_spec = selected_command.get("args_spec", {})

        parsed = self.parse_args(raw_args, args_spec)

        try:
            selected_command["func"](parsed)
        except Exception as e:
            self.panic(f"An error occurred while executing the command: {e}")
