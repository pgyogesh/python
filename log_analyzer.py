#!/usr/bin/env python
import re
import optparse
import datetime

parser = optparse.OptionParser()
parser.add_option("-f","--file",dest="log_file",
                          action="store",help="Specify log file to be parsed")
options, args = parser.parse_args()
vLogFile=options.log_file

hour = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']

def get_errors():
    counter = 0
    for h in hour:
        error_regex= '^^\d\d\d\d-\d\d-\d\d %s:\d\d:\d\d.\d\d\d Error:' %h
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
        error_regex= '^\d\d\d\d-\d\d-\d\d %s:\d\d:\d\d.\d\d\d Warning:' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def get_notices():
    counter = 0
    for h in hour:
        error_regex= '^\d\d\d\d-\d\d-\d\d %s:\d\d:\d\d.\d\d\d Notice:' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def get_criticals():
    counter = 0
    for h in hour:
        error_regex= '^\d\d\d\d-\d\d-\d\d %s:\d\d:\d\d.\d\d\d Critical:' %h
        file = open(vLogFile,"r")
        for line in file:
            for match in re.finditer(error_regex,line,re.S):
                counter = counter + 1
        if counter != 0:
            print(h,':',counter * '*',counter)
        counter = 0
        file.close()

def trim_log():
    start_time = input("Please enter start time:\n[Format: HH:MM]=")
    end_time = input("Please enter end time:\n[Format: HH:MM]=")
    trim_time = datetime.datetime.now().strftime('%d%H%M%S')
    output_file = 'trimmed_log_%s.txt' %trim_time
    with open(vLogFile) as file:
        for vline in file:
            vDate = vline[0:10]
            break
        start_line = vDate + ' ' + start_time
        end_line = vDate + ' ' + end_time
        print("Start time:", start_line)
        print("End time:", end_line)
        for num, line in enumerate(file, 1):
            if start_line in line:
                start_line_number = num
                break
        for num, line in enumerate(file, 1):
            if end_line in line:
                end_line_number = num
                break
        file.close()
    with open(vLogFile,"r") as file:
        oFile = open(output_file,'a')
        for num, line in enumerate(file, 1):
            if num >= start_line_number and num <= end_line_number:
                oFile.write(line)
    print("%s Created" %output_file)
if __name__ == '__main__':
    print("1. Error\n2. Warning\n3. Notice\n4. Critical")
    vChoice = int(input("Please choose your option from above options (Ex. Choose 2 for Warnings)\n="))
    if vChoice == 1:
        get_errors()
    elif vChoice == 2:
        get_warnings()
    elif vChoice == 3:
        get_notices()
    elif vChoice == 4:
        get_criticals()
    else:
        print("Wrong input.. Exiting...!")
    trim_choice = input("Do you want to trim error log:Y|N[Default=N]\n=")
    if trim_choice == 'Y':
        trim_log()
    else:
        print("Exiting on user request")
