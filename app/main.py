import sys
import os

import subprocess
def main():
    
    builtins=["echo","exit","type","pwd","cd"]
    
    while True:
        
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command=input()
        
        parts =command.split()
        
        cmd = parts[0]
        
        # echo prints
        if command.startswith("echo "):
            print(command[5:])
            continue
        
        #exit 
        elif command=="exit":
            break
        
        # print working directory
        elif command =="pwd":
            print(os.getcwd())

        # change directory
        elif command == "cd":

            if len(parts) < 2:
                continue

            path=parts[1]

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

                    subprocess.run(parts)

                    found=True
                    break
            
            if not found:
                print(f"{cmd}: command not found")



        

    
    pass



if __name__ == "__main__":
    main()
