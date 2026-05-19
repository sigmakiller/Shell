import sys

def main():
   
    
    
    while True:
        sys.stdout.write("$ ")
        command=input()
        if command.startswith("echo "):
            print(command[5:])
            continue
        elif command=="exit":
            break
        print(f"{command}: command not found")
        
    pass



if __name__ == "__main__":
    main()
