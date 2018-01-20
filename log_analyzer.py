import re
import optparse

parser = optparse.OptionParser()
parser.add_option("-f","--file",dest="log_file",
                          action="store",help="Specify log file to be parsed")
options, args = parser.parse_args()
vLogFile=options.log_file

hour = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']

def get_errors():
    counter = 0
    for h in hour:
        error_regex= '^%s:\d\d-ERROR' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def get_warnings():
    counter = 0
    for h in hour:
        error_regex= '^%s:\d\d-WARNING' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def get_fatals():
    counter = 0
    for h in hour:
        error_regex= '^%s:\d\d-FATAL' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def get_panics():
    counter = 0
    for h in hour:
        error_regex= '^%s:\d\d-PANIC' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

if __name__ == '__main__':
    print("1. Error\n2. Warning\n3. Fatal\n4. Panic")
    vChoice = int(input("Please choose your option from above options (Ex. Choose 2 for Warnings)\nOption="))
    if vChoice == 1:
        get_errors()
    elif vChoice == 2:
        get_warnings()
    elif vChoice == 3:
        get_fatals()
    elif vChoice == 4:
        get_panics()
    else:
        print("Wrong input.. Exiting...!")
