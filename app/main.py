import sys
import os
import shlex
import subprocess
import tty
import termios

BUILTINS = ["echo", "exit", "type", "pwd", "cd","complete","jobs"]

completion_specs={}
job_counter = 1
jobs_list = []

def reap_jobs():
    global jobs_list

    remaining_jobs = []

    for job in jobs_list:

        if job["process"].poll() is None:

            remaining_jobs.append(job)

        else:

            print(
                f"[{job['job_id']}]+  {'Done':<24}{job['command'].replace(' &', '')}"
            )

    jobs_list = remaining_jobs




def execute_command(command):
    global job_counter
    
    builtins = ["echo", "exit", "type", "pwd", "cd","complete","jobs"]
    parts = shlex.split(command, posix=True)

    background = False

    if parts and parts[-1] == "&":
        background = True
        parts = parts[:-1]


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
    
    elif cmd=="complete":
    # Register
        if len(parts) >= 4 and parts[1] == "-C":

            script_path = parts[2]
            command_name = parts[3]

            completion_specs[command_name] = script_path

        # Remove
        elif len(parts) >= 3 and parts[1] == "-r":

            command_name = parts[2]

            if command_name in completion_specs:
                del completion_specs[command_name]      
    
    # Print    
        elif len(parts) >= 3 and parts[1] == "-p":

            command_name = parts[2]

            if command_name in completion_specs:

                print(
                    f"complete -C '{completion_specs[command_name]}' {command_name}"
                )

            else:

                print(
                    f"complete: {command_name}: no completion specification"
                )


    #Background Jobs    
    elif cmd == "jobs":

        reap_jobs()

        running_jobs = [
            job for job in jobs_list
            if job["process"].poll() is None
        ]   

    # remove completed jobs AFTER printing them
        jobs_list[:] = [
            job for job in jobs_list
            if job["process"].poll() is None
        ]   
    
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

                            if background:

                                proc = subprocess.Popen(
                            parts,
                                    stdout=out,
                                    stderr=err
                                )

                                jobs_list.append({
                                    "job_id": job_counter,
                                    "pid": proc.pid,
                                    "process": proc,
                                    "command": command,
                                })

                                print(f"[{job_counter}] {proc.pid}")
                                job_counter += 1

                            else:

                                subprocess.run(
                                    parts,
                                    stdout=out,
                                    stderr=err
                                )

                elif stdout_redirect:

                    with open(stdout_redirect, stdout_mode) as out:

                        if background:

                            proc = subprocess.Popen(
                                parts,
                                stdout=out
                            )

                            jobs_list.append({
                                "job_id": job_counter,
                                "pid": proc.pid,
                                "process": proc,
                                "command": command,
                            })

                            print(f"[{job_counter}] {proc.pid}")
                            job_counter += 1

                        else:

                            subprocess.run(
                                parts,
                                stdout=out
                            )

                elif stderr_redirect:

                    with open(stderr_redirect, stderr_mode) as err:

                        if background:

                            proc = subprocess.Popen(
                                parts,
                                stderr=err
                            )

                            jobs_list.append({
                                "job_id": job_counter,
                                "pid": proc.pid,
                                "process": proc,
                                "command": command,
                            })

                            print(f"[{job_counter}] {proc.pid}")
                            job_counter += 1

                        else:

                            subprocess.run(
                                parts,
                                stderr=err
                            )

                else:

                    if background:

                        proc = subprocess.Popen(parts)

                        jobs_list.append({
                            "job_id": job_counter,
                            "pid": proc.pid,
                            "process": proc,
                            "command": command,
                        })

                        print(f"[{job_counter}] {proc.pid}")
                        job_counter += 1

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


def longest_common_prefix(strings):
    if not strings:
        return ""

    prefix = strings[0]

    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]

    return prefix

def read_line():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    buffer = ""
    last_prefix = ""
    tab_count = 0

    try:
        tty.setraw(fd)

        while True:
            ch = sys.stdin.read(1)

            # Enter
            if ch in ("\r", "\n"):
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                return buffer

            # Backspace
            elif ch == "\x7f":
                if buffer:
                    buffer = buffer[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            # Tab
            elif ch == "\t":
                
 # Registered completer
                parts = buffer.split()

                if len(parts) >= 1:             

                    cmd = parts[0]

                    if cmd in completion_specs:

                        if buffer.endswith(" "):
                            current_word = ""
                            previous_word = parts[-1]
                        else:
                            current_word = parts[-1]

                            if len(parts) >= 2:
                                previous_word = parts[-2]
                            else:
                                previous_word = ""

                        try:

                            env = os.environ.copy()
                            env["COMP_LINE"] = buffer
                            env["COMP_POINT"] = str(len(buffer))

                            result = subprocess.run(
                                [
                                    completion_specs[cmd],
                                    cmd,
                                    current_word,
                                    previous_word,
                                ],
                                capture_output=True,
                                text=True,
                                env=env
                            )

                            candidates = sorted(
                                [c.strip() for c in result.stdout.splitlines() if c.strip()]
                            )

            # One candidate
                            if len(candidates) == 1:

                                candidate = candidates[0]

                                if current_word:

                                    remainder = candidate[len(current_word):]

                                    sys.stdout.write(remainder + " ")
                                    sys.stdout.flush()

                                    buffer += remainder + " "

                                else:

                                    sys.stdout.write(candidate + " ")
                                    sys.stdout.flush()

                                    buffer += candidate + " "

                                continue

            # Multiple candidates
                            elif len(candidates) > 1:

                                lcp = longest_common_prefix(candidates)

                # LCP extends current input
                                if len(lcp) > len(current_word):

                                    remainder = lcp[len(current_word):]

                                    sys.stdout.write(remainder)
                                    sys.stdout.flush()

                                    buffer += remainder

                                else:

                                    if buffer == last_prefix:
                                        tab_count += 1
                                    else:
                                        last_prefix = buffer
                                        tab_count = 1

                    # First TAB -> bell
                                    if tab_count == 1:

                                        sys.stdout.write("\a")
                                        sys.stdout.flush()

                    # Second TAB -> show candidates
                                    else:

                                        sys.stdout.write("\r\n")
                                        sys.stdout.write("  ".join(candidates))
                                        sys.stdout.write("\r\n")
                                        sys.stdout.write("$ " + buffer)
                                        sys.stdout.flush()

                                        tab_count = 0

                                continue

                        except Exception:
                            pass                            

  
                if " " in buffer or buffer.endswith(" "):

                    if buffer.endswith(" "):
                        token = ""
                    else:
                        token = buffer.split()[-1]

                    if "/" in token:

                        dir_path, prefix = token.rsplit("/", 1)

                        try:
                            matches = []

                            for entry in os.listdir(dir_path):
                                if entry.startswith(prefix):
                                    matches.append(entry)

                        except OSError:
                            matches = []

                    else:

                        prefix = token

                        matches = []

                        for entry in os.listdir("."):
                            if entry.startswith(prefix):
                                matches.append(entry)

                    matches.sort()

                    if len(matches) == 1:

                        completion = matches[0]

                        if "/" in token:
                            full_match = os.path.join(dir_path, completion)
                        else:
                            full_match = completion

                        remainder = completion[len(prefix):]

                        if os.path.isdir(full_match):
                            sys.stdout.write(remainder + "/")
                            sys.stdout.flush()
                            buffer += remainder + "/"
                        else:
                            sys.stdout.write(remainder + " ")
                            sys.stdout.flush()
                            buffer += remainder + " "

                        continue
                    elif len(matches) > 1:

                        lcp = longest_common_prefix(matches)

    # LCP extends what user already typed
                        if len(lcp) > len(prefix):

                            remainder = lcp[len(prefix):]

                            sys.stdout.write(remainder)
                            sys.stdout.flush()

                            buffer += remainder

                        else:

                            if token == last_prefix:
                                tab_count += 1
                            else:
                                last_prefix = token
                                tab_count = 1

                            if tab_count == 1:

                                sys.stdout.write("\a")
                                sys.stdout.flush()

                            else:

                                display_matches = []

                                for match in sorted(matches):

                                    if "/" in token:
                                        full_path = os.path.join(dir_path, match)
                                    else:
                                        full_path = match

                                    if os.path.isdir(full_path):
                                        display_matches.append(match + "/")
                                    else:
                                        display_matches.append(match)

                                sys.stdout.write("\r\n")
                                sys.stdout.write("  ".join(display_matches))
                                sys.stdout.write("\r\n")
                                sys.stdout.write("$ " + buffer)
                                sys.stdout.flush()

                                tab_count = 0                                  
                matches = []

                for cmd in BUILTINS:
                    if cmd.startswith(buffer):
                        matches.append(cmd)

                for exe in get_executables():
                    if exe.startswith(buffer):
                        matches.append(exe)

                matches = sorted(set(matches))

                # No matches
                if len(matches) == 0:
                    sys.stdout.write("\a")
                    sys.stdout.flush()

                # Single match
                elif len(matches) == 1:

                    completion = matches[0]

                    if completion != buffer:
                        remainder = completion[len(buffer):] + " "

                        sys.stdout.write(remainder)
                        sys.stdout.flush()

                        buffer = completion + " "

# Multiple matches
                else:

                    lcp = longest_common_prefix(matches)

                    if len(lcp) > len(buffer):

                        completion = lcp[len(buffer):]

                        sys.stdout.write(completion)
                        sys.stdout.flush()

                        buffer = lcp

                        
                    else:

                        if buffer == last_prefix:
                            tab_count += 1
                        else:
                            last_prefix = buffer
                            tab_count = 1

                        if tab_count == 1:
                            sys.stdout.write("\a")
                            sys.stdout.flush()

                        else:
                            sys.stdout.write("\r\n")
                            sys.stdout.write("  ".join(matches))
                            sys.stdout.write("\r\n")
                            sys.stdout.write("$ " + buffer)
                            sys.stdout.flush()

                            tab_count = 0
            else:
                buffer += ch
                sys.stdout.write(ch)
                sys.stdout.flush()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():



    while True:

        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            command = read_line()
        except EOFError:
            break

        execute_command(command)

        reap_jobs()


if __name__ == "__main__":
    main()