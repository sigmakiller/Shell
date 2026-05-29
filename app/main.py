import sys
import os
import shlex
import subprocess


def main():

    builtins = ["echo", "exit", "type", "pwd", "cd"]

    while True:

        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            command = input()
        except EOFError:
            break

        parts = shlex.split(command, posix=True)

        if len(parts) == 0:
            continue

        stdout_redirect = None
        stderr_redirect = None

        if "2>" in parts:
            idx = parts.index("2>")
            stderr_redirect = parts[idx + 1]
            parts = parts[:idx]

        elif "1>" in parts:
            idx = parts.index("1>")
            stdout_redirect = parts[idx + 1]
            parts = parts[:idx]

        elif ">" in parts:
            idx = parts.index(">")
            stdout_redirect = parts[idx + 1]
            parts = parts[:idx]

        if len(parts) == 0:
            continue

        cmd = parts[0]

        # echo
        if cmd == "echo":

            output = " ".join(parts[1:])

            if stdout_redirect:
                with open(stdout_redirect, "w") as f:
                    f.write(output + "\n")
            else:
                print(output)

            if stderr_redirect:
                open(stderr_redirect, "w").close()

            continue

        # exit
        elif cmd == "exit":
            break

        # pwd
        elif cmd == "pwd":

            output = os.getcwd()

            if stdout_redirect:
                with open(stdout_redirect, "w") as f:
                    f.write(output + "\n")
            else:
                print(output)

            if stderr_redirect:
                open(stderr_redirect, "w").close()

        # cd
        elif cmd == "cd":

            if len(parts) < 2:
                continue

            path = os.path.expanduser(parts[1])

            if os.path.isdir(path):
                os.chdir(path)
            else:
                error_msg = f"cd: {parts[1]}: No such file or directory"

                if stderr_redirect:
                    with open(stderr_redirect, "w") as f:
                        f.write(error_msg + "\n")
                else:
                    print(error_msg)

        # type
        elif cmd == "type":

            if len(parts) < 2:
                continue

            target = parts[1]

            if target in builtins:
                output = f"{target} is a shell builtin"
            else:

                paths = os.environ["PATH"].split(":")
                output = None

                for path in paths:

                    full_path = os.path.join(path, target)

                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        output = f"{target} is {full_path}"
                        break

                if output is None:
                    output = f"{target}: not found"

            if stdout_redirect:
                with open(stdout_redirect, "w") as f:
                    f.write(output + "\n")
            else:
                print(output)

            if stderr_redirect:
                open(stderr_redirect, "w").close()

        # external commands
        else:

            paths = os.environ["PATH"].split(":")
            found = False

            for path in paths:

                full_path = os.path.join(path, cmd)

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):

                    if stdout_redirect and stderr_redirect:

                        with open(stdout_redirect, "w") as out:
                            with open(stderr_redirect, "w") as err:
                                subprocess.run(parts, stdout=out, stderr=err)

                    elif stdout_redirect:

                        with open(stdout_redirect, "w") as out:
                            subprocess.run(parts, stdout=out)

                    elif stderr_redirect:

                        with open(stderr_redirect, "w") as err:
                            subprocess.run(parts, stderr=err)

                    else:

                        subprocess.run(parts)

                    found = True
                    break

            if not found:
                error_msg = f"{cmd}: command not found"

                if stderr_redirect:
                    with open(stderr_redirect, "w") as f:
                        f.write(error_msg + "\n")
                else:
                    print(error_msg)


if __name__ == "__main__":
    main()