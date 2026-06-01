import sys
import os
import shlex
import subprocess
import readline

BUILTINS = ["echo", "exit"]


def execute_command(command):
    builtins = ["echo", "exit", "type", "pwd", "cd"]
    parts = shlex.split(command, posix=True)

    if not parts:
        return

    stdout_redirect = None
    stderr_redirect = None

    stdout_mode = "w"
    stderr_mode = "w"

        # stdout append
    if "1>>" in parts:
        idx = parts.index("1>>")
        stdout_redirect = parts[idx + 1]
        stdout_mode = "a"
        parts = parts[:idx]

    elif ">>" in parts:
        idx = parts.index(">>")
        stdout_redirect = parts[idx + 1]
        stdout_mode = "a"
        parts = parts[:idx]
        # stderr append
    elif "2>>" in parts:
        idx = parts.index("2>>")
        stderr_redirect = parts[idx + 1]
        stderr_mode = "a"
        parts = parts[:idx]

        # stdout overwrite
    elif "1>" in parts:
        idx = parts.index("1>")
        stdout_redirect = parts[idx + 1]
        stdout_mode = "w"
        parts = parts[:idx]

    elif ">" in parts:
        idx = parts.index(">")
        stdout_redirect = parts[idx + 1]
        stdout_mode = "w"
        parts = parts[:idx]

        # stderr overwrite
    elif "2>" in parts:
        idx = parts.index("2>")
        stderr_redirect = parts[idx + 1]
        stderr_mode = "w"
        parts = parts[:idx]

    if not parts:
        return

    cmd = parts[0]

        # echo
    if cmd == "echo":
        output = " ".join(parts[1:])

        if stdout_redirect:
            with open(stdout_redirect, stdout_mode) as f:
                f.write(output + "\n")
        else:
            print(output)

        if stderr_redirect:
            open(stderr_redirect, stderr_mode).close()

        # exit
    elif cmd == "exit":
        sys.exit(0)

        # pwd
    elif cmd == "pwd":
        output = os.getcwd()

        if stdout_redirect:
            with open(stdout_redirect, stdout_mode) as f:
                f.write(output + "\n")
        else:
            print(output)

        # cd
    elif cmd == "cd":

        if len(parts) < 2:
            return

        path = os.path.expanduser(parts[1])

        if os.path.isdir(path):
            os.chdir(path)
        else:
            error_msg = f"cd: {parts[1]}: No such file or directory"

            if stderr_redirect:
                with open(stderr_redirect, stderr_mode) as f:
                    f.write(error_msg + "\n")
            else:
                print(error_msg)

        # type
    elif cmd == "type":

        if len(parts) < 2:
            return

        target = parts[1]

        if target in builtins:
            output = f"{target} is a shell builtin"
        else:
            output = None

            for path in os.environ["PATH"].split(":"):

                full_path = os.path.join(path, target)

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    output = f"{target} is {full_path}"
                    break

            if output is None:
                output = f"{target}: not found"

        if stdout_redirect:
            with open(stdout_redirect, stdout_mode) as f:
                f.write(output + "\n")
        else:
            print(output)

        # external commands
    else:

        found = False

        for path in os.environ["PATH"].split(":"):

        full_path = os.path.join(path, cmd)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):

                if stdout_redirect and stderr_redirect:

                    with open(stdout_redirect, stdout_mode) as out:
                        with open(stderr_redirect, stderr_mode) as err:
                            subprocess.run(parts, stdout=out, stderr=err)

                elif stdout_redirect:

                    with open(stdout_redirect, stdout_mode) as out:
                        subprocess.run(parts, stdout=out)

                elif stderr_redirect:

                    with open(stderr_redirect, stderr_mode) as err:
                        subprocess.run(parts, stderr=err)

                else:

                    subprocess.run(parts)

                found = True
                break

        if not found:

            error_msg = f"{cmd}: command not found"

            if stderr_redirect:
                with open(stderr_redirect, stderr_mode) as f:
                    f.write(error_msg + "\n")
            else:
                print(error_msg)


def get_executables():
    executables = set()

    for path in os.environ.get("PATH", "").split(":"):

        if not os.path.isdir(path):
            continue

        try:
            for file in os.listdir(path):

                full_path = os.path.join(path, file)

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    executables.add(file)

        except OSError:
            pass

    return executables


def completer(text, state):
    matches = []

    for cmd in BUILTINS:
        if cmd.startswith(text):
            matches.append(cmd)

    for exe in get_executables():
        if exe.startswith(text):
            matches.append(exe)

    matches.sort()

    if state < len(matches):
        return matches[state]

    return None
readline.set_completer(completer)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set show-all-if-ambiguous on")


def main():
    

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            command = input()
        except EOFError:
            break

        


if __name__ == "__main__":
    main()