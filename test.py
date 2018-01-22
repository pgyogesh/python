import re
import sys
import optparse
import datetime

parser = optparse.OptionParser()
parser.add_option("-f","--file",dest="log_file",
                          action="store",help="Specify log file to be parsed")
options, args = parser.parse_args()
vLogFile=options.log_file

#2018-01-21 00:49:43
#2018-01-21 23:33:05

#start_time = 00:50
#end_time = 22:00
#2018-01-22 00:00:00.112 Error: TaskServerTask::run: XDMP-NODB: No database with identifier 8686852932750358913
def trim_log():
    start_time = input("Please enter start time:\n[Format: HH:MM]=")
    end_time = input("Please enter end time:\n[Format: HH:MM]=")
    trim_time = datetime.datetime.now().strftime('%d%H%M%S')
    output_file = 'trimmed_log_%s' %trim_time
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
