from netmiko import ConnectHandler
from getpass import getpass
from getpass import getuser
import regex as re
import time
from colorama import init, Fore, Back, Style
import os
#################################
st = time.time()
init()

absolute_path = os.path.dirname(__file__)
relative_path = absolute_path + "\\" + "Result files" + "\\"









def createList(r1, r2):
    return list(range(r1, r2+1))
    

def Str_To_Int(the_list):
    vlan_int_list = []
    for item in the_list:
        vlan_int_list.append(int(item))
    
    return vlan_int_list

def Compare(vlan_brief_list, vlan_access_result, vlan_allowed_result, vlan_mgmt_result):
    All_Used_Vlan = list(set(vlan_access_result + vlan_allowed_result + vlan_mgmt_result))
    All_Used_Vlan.sort()
    vlan_excess = list(set(vlan_brief_list) - set(All_Used_Vlan))


    vlan_excess = list(set(vlan_brief_list) - set(All_Used_Vlan))
    vlan_shortage = list(set(All_Used_Vlan) - set(vlan_brief_list))
    vlan_excess.sort()
    vlan_shortage.sort()
    
    return vlan_excess,vlan_shortage








class Shows:
    
    def __init__(self, Devices):
        self.show_allowed_vlan = "show run | i allowed vlan"
        self.show_access_vlan = "show run | i access vlan "
        self.show_vlan_brief = "show vlan brief"
        self.show_mgmt_vlan = "show int description | i Vl"
        self.Devices = Devices


    def Vlan_Mgmt_Result(self):
        mgmt_vlan_numbers = []
        # Send Command
        show_vlan_mgmt_output = net_connect.send_command(self.show_mgmt_vlan)
        line_splited_show_vlan_mgmt_output = TextToTable(show_vlan_mgmt_output)
        line_splited_show_vlan_mgmt_output_inc = line_splited_show_vlan_mgmt_output.Line_Split_Strip()

        for item in line_splited_show_vlan_mgmt_output_inc:
            mgmt_vlan = re.findall(r"\d+", item[0])
            mgmt_vlan_numbers.append(int(mgmt_vlan[0]))
        vlan_mgmt_numbers_unique = list(set(mgmt_vlan_numbers))
        vlan_mgmt_numbers_unique.sort()
        result = Str_To_Int(vlan_mgmt_numbers_unique)
        
        return result


    def Vlan_Brief_Result(self):
        vlan_numbers = []  
        # Send Command
        # with ConnectHandler(**Device_connection_info) as net_connect:
        show_vlan_brief_output = net_connect.send_command(self.show_vlan_brief)
        line_splited_show_vlan_brief_output = show_vlan_brief_output.splitlines()

        line_splited_show_vlan_brief_output = line_splited_show_vlan_brief_output[3:]
        # print(line_splited_show_vlan_brief_output)
        for item in line_splited_show_vlan_brief_output:
            # print(item)
            vlan_number = re.findall(r"^\d+", item)
            if vlan_number:
                # print(vlan_number)
                vlan_numbers.append(int(vlan_number[0]))
            else:
                pass
        vlan_numbers_unique_set = set(vlan_numbers)
        
        vlan_numbers_unique_set.remove(1002)
        vlan_numbers_unique_set.remove(1003)
        vlan_numbers_unique_set.remove(1004)
        vlan_numbers_unique_set.remove(1005)
        vlan_numbers_unique = list(vlan_numbers_unique_set)
        vlan_numbers_unique.sort()
        result = Str_To_Int(vlan_numbers_unique)
        
        return result


    def Vlan_Access_Result(self):
        acc_vlan_numbers = []  
        # Send Command
        # with ConnectHandler(**Device_connection_info) as net_connect:
        show_vlan_access_output = net_connect.send_command(self.show_access_vlan)
        line_splited_show_vlan_acc_output = show_vlan_access_output.splitlines()
        #print(line_splited_show_vlan_brief_output)
        for item in line_splited_show_vlan_acc_output:
            acc_vlan_number = re.findall(r"\d+", item)
            acc_vlan_numbers.append(int(acc_vlan_number[0]))
        acc_vlan_numbers_unique = list(set(acc_vlan_numbers))
        acc_vlan_numbers_unique.sort()
        result = Str_To_Int(acc_vlan_numbers_unique)
        
        return result


    def Vlan_Allowed_Result(self):
        alwd_vlan_numbers = []  
        # Send Command
        # with ConnectHandler(**Device_connection_info) as net_connect:
        show_vlan_allowed_output = net_connect.send_command(self.show_allowed_vlan)
        line_splited_show_vlan_alwd_output = TextToTable(show_vlan_allowed_output)
        line_splited_show_vlan_mgmt_output_inc = line_splited_show_vlan_alwd_output.Line_Split_Strip()
        #print(line_splited_show_vlan_alwd_output)
        for item in line_splited_show_vlan_mgmt_output_inc:        
            alwd_vlan_with_comma = re.split(r',', item[-1])
            if alwd_vlan_with_comma == int:
                for alwd_vlan in alwd_vlan_with_comma:
                    if "-" in alwd_vlan:
                        range = alwd_vlan.split("-")
                        # print(range)
                        r1 = int(range[0])
                        r2 = int(range[-1])
                        range_list = createList(r1, r2)
                        for vlan_in_range in range_list:
                            alwd_vlan_numbers.append(int(vlan_in_range))
                    else:
                        alwd_vlan_numbers.append(int(alwd_vlan))
                else:
                    pass
        alwd_vlan_numbers_unique = list(set(alwd_vlan_numbers))
        alwd_vlan_numbers_unique.sort()
        result = Str_To_Int(alwd_vlan_numbers_unique)
        
        return result


    def __str__(self):
        return f"This Class processes show's result and returns list of VLANs that shoud be compared."




class File:

    def __init__(self, filename):
    # Open devices file
        self.filename = filename


    def Open_file(self):
        print(self.filename)
        Obj_file_open = open(str(self.filename), 'r')
        Object_file = Obj_file_open.read()
        Obj_file_open.close()
        Linesplited_obj = Object_file.splitlines()
        Obj_list = []
        for obj in Linesplited_obj:
            striped_obj = obj.strip()
            Obj_list.append(striped_obj)
        
        return Obj_list


    def __str__(self):
        return f"This Class, returns all objects in the input file with list of readable object (without any space)"




class TextToTable:

    def __init__(self, textlist):
        self.textlist = textlist


    def Line_Split_Strip(self):
        linesplited_item = self.textlist.splitlines()
        Items = []
        for item in linesplited_item:
            striped_item = item.strip()
            columnsplited_item = re.split(r'\s+', striped_item)
            Items.append(columnsplited_item)
            # print(Items)       
        
        return Items




class PrintToFile:

    def __init__(self,file_path, vlan_excess,vlan_shortage):
        self.file_path = file_path
        self.vlan_excess = vlan_excess
        self.vlan_shortage = vlan_shortage
        self.device = device


    def Print(self):
        # Write Sub Interface That Are Configured In Device Into A List 
        with open(str(self.file_path), 'w') as f:
            if self.vlan_excess:
                f.write(f'### The VLANs that are in switch\'s vlan database (show vlan brief) but it\'s NOT configured under any interface ###\n')
                for item in self.vlan_excess:
                    f.write(f"{item}\n")
            else:
                pass
            
            if self.vlan_shortage:
                f.write(f'#### The VLANs that are configured under interfaces but there aren\'t in vlan database (show vlan brief) ###\n')
                for item in self.vlan_shortage:
                    f.write(f"{item}\n")
            else:
                pass
            f.close()


    def Output(self):
        
        print(("-" * 50) + device + ("-" * 50))
        if self.vlan_excess:
            print(f'### The VLANs that are in switch\'s vlan database (show vlan brief) but it\'s NOT configured under any interface ###')
            for item in self.vlan_excess:
                print(f"{item}")
        else:
            pass
            
        if self.vlan_shortage:
            print(f'#### The VLANs that are configured under interfaces but there aren\'t in vlan database (show vlan brief) ###')
            for item in self.vlan_shortage:
                print(f"{item}")
        else:
            pass
        print("\n")


    def __str__(self):
        return f"This class writes the final result into file"



class Messages:

    def Banner(self):
        
        print("""
  _   _  ____   _____    _____           _       _   
 | \\ | |/ __ \\ / ____|  / ____|         (_)     | |  
 |  \\| | |  | | |      | (___   ___ _ __ _ _ __ | |_ 
 | . ` | |  | | |       \\___ \\ / __| '__| | '_ \\| __|
 | |\\  | |__| | |____   ____) | (__| |  | | |_) | |_ 
 |_| \\_|\\____/ \\_____| |_____/ \\___|_|  |_| .__/ \\__|
                                          | |        
                                          |_|         """)


    def Warning(self):
        print("""
        WARNING: This script is intended for use by experienced users only.
                 Running this script without having knowledge may result in significant changes to your network.        
                 By continuing, you acknowledge that you understand the risks and accept full responsibility for any consequences.
                """)


    def Copyright(self):
        print ("""
         © Reproduction and distribution of this script without wirtten or verbal permission of AmirHossein Khalilpour is prohibited,
         violators will be prosecuted to the fullest extent of both civil and criminal law.\n""")


    def ScriptInfo(self):
        print ("""
         Script name : Vlan Database Checker\n\n""")
    

    def EndMessage(self):
        print ("Time to run script : ", elapsed_time, "\n")
        group_a = Style.BRIGHT+Fore.RED+"G"+Style.RESET_ALL+Style.BRIGHT+Fore.CYAN+"r"+Style.RESET_ALL+Style.BRIGHT+Fore.YELLOW+"o"+Style.RESET_ALL+Style.BRIGHT+Fore.GREEN+"u"+Style.RESET_ALL+Style.BRIGHT+Fore.WHITE+"p "+Style.RESET_ALL+Style.BRIGHT+Fore.MAGENTA+"A"+Style.RESET_ALL
        print ((group_a + "\n") * 5)


    def __str__(self):
        return f" This class is used to show common messages in each script."



messages = Messages()
messages.Banner()
messages.Warning()
messages.Copyright()
messages.ScriptInfo()

while True:
   
    device_list_path = input("Please specify the Devices DNS file path. Otherwise to use default list press ENTER: ")
    if device_list_path == "":
        device_list_path = absolute_path + "\\" + "Devices.txt"
    else:
        pass
    
    
    try:
        Devicing = File(device_list_path)
        Devices = Devicing.Open_file()
    except Exception as error:
        print("An error occurred:", error)
        break


    print("\nDevices List:\n")
    for line in Devices:
        print (line)


    confirmation = input("\nList of all devices DNS are as below, do you confirm it? [yes/no] ")
    if confirmation == "yes":     
        print ("\n")
        Username = input('\nPlease enter your username:')
        Password = getpass('Please enter your password:')

        for device in Devices:            
            file_path = relative_path + device + '.txt'
            Device_connection_info = { 
                "device_type": "cisco_ios",
                "host": str(device),
                "username": Username,
                "password": Password,
                }
            
                        
            try:
                with ConnectHandler(**Device_connection_info) as net_connect:
                    
                    device_instances = Shows(device)
                    vlan_brief_list = device_instances.Vlan_Brief_Result()
                    vlan_access_result = device_instances.Vlan_Access_Result()
                    vlan_allowed_result = device_instances.Vlan_Allowed_Result()
                    vlan_mgmt_result = device_instances.Vlan_Mgmt_Result()

                    vlan_excess,vlan_shortage = Compare(vlan_brief_list, vlan_access_result, vlan_allowed_result, vlan_mgmt_result)

                    result = PrintToFile(file_path,vlan_excess,vlan_shortage)
                    result.Print()
                    result.Output()
                    
            except Exception as error:
                print(("-" * 50) + device + ("-" * 50))
                print("An error occurredfullt:", error)
                pass            
        break
    else:
        pass


et = time.time()
elapsed_time = et - st

messages.EndMessage()