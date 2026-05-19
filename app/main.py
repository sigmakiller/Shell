import sys

def main():
   
    
    sys.stdout.write("$ ")
    while True:
        command=input()
        print(f"{command}: command not found")
    
    pass



if __name__ == "__main__":
    main()
