import cmd
import sys
import os
import shlex
import subprocess
def main():
    
    builtins=["echo","exit","type","pwd","cd"]
    
    while True:
        
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            command = input()
        except EOFError:
            break
        
        parts =shlex.split(command,posix=True)
        
        if len(parts)==0:
            continue

        #Handle stdout redirection
        redirect_file =None

        if  ">" in parts:
            idx = parts.index(">")
            redirect_file = parts[idx+1]
            parts = parts[:idx]


        elif "1>" in parts:
            idx = parts.index(">")
            redirect_file = parts[idx+1]
            parts = parts[:idx]      
        
        
        
        if len(parts) == 0:
            continue
        
        cmd = parts[0]
        
        # echo prints
        if cmd == "echo":
            print(" ".join(parts[1:]))
            continue
        
        #exit 
        elif cmd =="exit":
            break
        
        # print working directory
        elif cmd =="pwd":
            print(os.getcwd())

        # change directory
        elif cmd == "cd":

            if len(parts) < 2:
                continue

            path=parts[1]

            if path == "~":
                path = os.environ["HOME"]

            if os.path.isdir(path):
                os.chdir(path)

            else:
                print(f"cd: {path}: No such file or directory")


        # type check cmd is builtin or executable
        elif cmd == "type":

            if len(parts) < 2:
                continue

            target = parts[1]

            if target in builtins:
                print(f"{target} is a shell builtin")

            else:

                paths = os.environ["PATH"].split(":")

                found = False

                for path in paths:

                    full_path = os.path.join(path, target)

                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):

                        print(f"{target} is {full_path}")

                        found = True
                        break

                if not found:
                    print(f"{target}: not found")

        # executable programs
        else:

            paths= os.environ["PATH"].split(":")

            found = False

            for path in paths:

                full_path=os.path.join(path,cmd)

                if os.path.isfile(full_path) and os.access(full_path,os.X_OK):

                    if redirect_file:
                        with open(redirect_file, "w") as f:
                            subprocess.run(parts, stdout=f)
                    else:
                        subprocess.run(parts)

                    found=True
                    break
            
            if not found:
                print(f"{cmd}: command not found")



        

    
    pass



if __name__ == "__main__":
    main()
