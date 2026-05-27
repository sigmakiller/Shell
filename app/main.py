import sys
import os

import subprocess
def main():
    
    builtins=["echo","exit","type"]
    
    while True:
        
        sys.stdout.write("$ ")
        
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
            print(os.getcwd)

        #Search PATH
        elif command.startswith("type"):
            target = command[5: ]
            if target in builtins:
                print(f"{target} is a shell builtin")
            else:
                paths = os.environ["PATH"].split(":")

                found=False

                for path in paths:

                    full_path = os.path.join(path,target)

                    if os.path.isfile(full_path) and os.access(full_path,os.X_OK):

                        print(f"{target} is {full_path}")

                        found=True
                        break
                if not found:
                    print(f"{target}: not found")
            continue

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
