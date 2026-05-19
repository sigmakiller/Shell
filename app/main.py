import sys

from click import command


def main():
   
    
    sys.stdout.write("$ ")
    
    command=input()
    print(f"{command}:command not found")
    
    pass



if __name__ == "__main__":
    main()
