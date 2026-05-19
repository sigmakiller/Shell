import sys

def main():
   
    builtins=["echo","exit","type"]
    
    while True:
        sys.stdout.write("$ ")
        command=input()
        if command.startswith("echo "):
            print(command[5:])
            continue
        elif command=="exit":
            break
        elif command.startswith("type"):
            target = command[5: ]
            if target in builtins:
                print(f"{target}is a shell bulletin")
            else:
                print(f"{target}: not found")
            continue
        
        print(f"{command}: command not found")
        

    
    pass



if __name__ == "__main__":
    main()
