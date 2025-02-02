from netmiko import ConnectHandler
from getpass import getpass
from getpass import getuser
import regex as re
import time
from colorama import init, Fore, Back, Style



# Initialization
st = time.time()
init()


# Files Name
Device_list = "Devices.txt"
Commands_list = "Commands.txt"

# Show command that we execute.
show_int_desc = "show int desc"
show_run = "show run interface "

# Default lists
Deficiency = []




# Open and Clean the files
def Open_file(filename):
    Obj_file_open = open(str(filename), 'r')
    Object_file = Obj_file_open.read()
    Obj_file_open.close()
    Linesplited_obj = Object_file.splitlines()
    Obj_list = []
    for obj in Linesplited_obj:
        striped_obj = obj.strip()
        Obj_list.append(striped_obj)
    return Obj_list


# Files instance
try:
    Devices = Open_file(str(Device_list))
    Commands = Open_file(str(Commands_list))
except:
    print("\n!!! Something about openning file, went wrong.")




# Connection and getting "show interface description" from the device
def Desc_Show(device, device_connection_info):
      
        # Send Command
        with ConnectHandler(**device_connection_info) as net_connect:
            show_desc_output = net_connect.send_command(show_int_desc)

        # Split Output Into List Of Lines
        linesplited_show_output = show_desc_output.splitlines()
        Interfaces = []
        for interface in linesplited_show_output:
            Striped_line = interface.strip()
            columnsplited_output =  re.split(r'\s+', Striped_line)
            Interfaces.append(columnsplited_output[0])
        
        return Interfaces

# Connection and getting "show running-config" from the device
def Run_Show(Interfaces, device_connection_info):
        
        with ConnectHandler(**device_connection_info) as net_connect:
            Result = [device]
            for interface in Interfaces:         
                show_run_output = net_connect.send_command(show_run + interface)
                Compare_result = Compare(show_run_output)
                Compare_result.insert(0, interface)
                Result.append(Compare_result)
            return Result
                
                
# Check the commands exist under interfaces or not
def Compare(show_run_output):

    description = re.findall(r"\w+\.\w+\.\w+", show_run_output)
    Deficiency = [description[0]]
    for line in Commands:
        if not line in show_run_output:
            Deficiency.append(line)
        else:
            continue
    return Deficiency


# The final result that prints everything (version 2)
def Result_Show_2(Result):
    #print ("\n" + ("-" * 25) + Result[0] + " (Second Result)" + ("-" * 25) + "\n")
    #print("Device \"" + Back.YELLOW + Fore.BLACK + Result[0] + Style.RESET_ALL + "\" has below output:\n\n")
    for inf in Result[1:]:
        if len(inf) >= 3:
            print ("Interface : " + inf[0])
            print ("Description : " + inf[1] + "\n")
            print ("These commands are NOT configured on the interface :")
            for y in inf[2:]:
                print("\t" + y)
            else:
                print ( "\n" + Fore.RED + ("-" * 25) + "END of " + Result[0] + ("-" * 25))
                print(Style.RESET_ALL)

# The final result that prints everything (version 1)       
def Result_Show(Result):
    #print (f"\n" + ("-" * 25) + Result[0] + " (First Result)" + ("-" * 25) + "\n")
    #print("Device \"" + Back.YELLOW + Fore.BLACK + Result[0] + Style.RESET_ALL + "\" has below output:\n")
    for command in Commands:
        print ("\nCommand : " + Fore.RED + command + Style.RESET_ALL)
        for inf in Result[1:]:
            for x in inf[2:]:
                if command in x:
                    print (inf[0], end =", ")
        else:
            continue


# Check that the Username and Password is valid or not. It repeats 3 times.
# The host must be a device that can authenticate with most availability in the network 
count = 0
while count < 3 :
    try:
        Username = input('\nPlease enter your username:')
        Password = getpass('Please enter your password:')
        info = { 
        "device_type": "cisco_ios",
        "host": "ExampleDeviceName.local",
        "username": Username,
        "password": Password,
        }        
        with ConnectHandler(**info) as net_connect:
            net_connect.disconnect
        
        count = 3
    except Exception as error:
        pass
        print("An error occurred:", error)
        count += 1



# The main part of script which runs the functions
for device in Devices:
    
    device_connection_info = { 
        "device_type": "cisco_ios",
        "host": str(device),
        "username": Username,
        "password": Password,
        }
    try:
        print ("\n" + ("-" * 25) + str(device) + ("-" * 25) + "\n")
        print("Device \"" + Back.YELLOW + Fore.BLACK + str(device) + Style.RESET_ALL + "\" has below output:\n\n")
        x = Desc_Show(device, device_connection_info)
        y = Run_Show(x, device_connection_info)
        Result_Show(y)
        print ("\n" * 2)            
    except Exception as error:
        print("An error occurred:", error)
        print ("\n" * 2)
        pass
    

# Done Message
print ("\n" * 1)
print("!!!!! Its Done !!!!!")

# Script's informations
et = time.time()
elapsed_time = et - st
print ("\nScript name : Interface's Sub Commands Standadrds")
print ("Time to run script : ", end = " ")
print (elapsed_time)