#!/bin/env python
from multiprocessing import Pool, Value
from pygresql.pg import DB
import optparse
from gppylib import gplog
import datetime
import re
import os
import sys
import smtplib


# Command line options
help_usage = """
python2 paralled_restore.py -d <database_name> -u <backup_files_directory> -t <dump_key> -p <number of parallel processes"""

parser = optparse.OptionParser(usage=help_usage)
parser.add_option("-d", "--database", dest="database", action="store", help="Specify target database to restore backup")
parser.add_option("--host", dest="host",action="store", default='localhost', help="Specify the target host")
parser.add_option("-t", "--timestamp", dest="timestamp", action="store", help="Specify the timestamp of backup")
parser.add_option("-p", "--parallel-processes",dest="parallel", action="store", default=1, help="Specify number of parallel-processes")
parser.add_option("-u", "--directory", dest="directory", action="store", help="Specify Backup directory")
parser.add_option("--noanalyze", dest="noanalyze", action="store_true", help="Specify if you dont want to run analyze on restored database")
options, args = parser.parse_args()

# Program logging
logger = gplog.get_default_logger()
gplog.setup_tool_logging("parallel_restore", '', "gpadmin")

# Start

logger.info("Starting script with args " + str(' '.join(sys.argv)))

# Python version check
if sys.version_info[0] != 2:
    logger.error("This script only supported by Python version 2... Exiting")
    sys.exit()

# Validating command line options

if options.timestamp:
    vDump_key = options.timestamp
else:
    logger.error("timestamp not supplied... exiting...")
    sys.exit()

if options.database:
    vDatabase = options.database
else:
    logger.error("database not supplied... exiting...")
    sys.exit()

if options.directory:
    vDirectory = options.directory
else:
    logger.error("directory not supplied... exiting...")
    sys.exit()

con = DB(dbname='gpadmin', host=options.host)
if vDatabase in con.get_databases():
    pass
else:
    logger.error("Database doesn't exists... exiting")
    sys.exit()
con.close()

vProcesses = int(options.parallel)
vHost = options.host

now = datetime.datetime.now()
vDate = str(now.strftime("%Y%m%d"))

logger.info("Getting list master file and segment files")

backup_files = os.listdir(vDirectory)
master_files = [vDirectory + '/' + 'gp_dump_-1_1_%s' %vDump_key, vDirectory + '/' + 'gp_dump_1_1_%s' %vDump_key]
segment_file_regex = 'gp_dump_\d+_\d+_%s$' %vDump_key

# Getting Master file
for file in master_files:
    if os.path.isfile(file):
        master_file = file
if master_file:
    pass
else:
    logger.error("Master file doesn't exists... Exiting...")
    sys.exit()

# Restoring master file
logger.info("Restoring master SQL file: %s" %master_file)
run_master_file = "psql %s -h %s -f %s >> /home/gpadmin/gpAdminLogs/parallel_restore_master_%s_%s.log 2>> /home/gpadmin/gpAdminLogs/parallel_restore_master_%s_%s.error" %(vDatabase, vHost, master_file, vDump_key, vDate, vDump_key, vDate)
os.popen(run_master_file)
logger.info("Restoring master SQL file completed")

# def sendmail(body):
#     SENDER = 'DBA-Greenplum@broadridge.com'
#     RECEIVERS = 'DBA-Greenplum@broadridge.com'
#     sender = SENDER
#     receivers = RECEIVERS
#
#     message = """From: """ + SENDER + """
# To: """ + RECEIVERS + """
# MIME-Version: 1.0
# Content-type: text/html
# Subject: Parallel restore status """ + vDatabase + """\n"""
#     message = message + body
#     try:
#         smtpObj = smtplib.SMTP('localhost')
#         smtpObj.sendmail(sender, receivers, message)
#     except SMTPException:
#         logging.error("Unable to send email")

# Get segment files to restore
def get_segment_files():
    segment_files = []
    for file in backup_files:
        if re.match(segment_file_regex, file, re.S):
            segment_files.append(vDirectory + '/' + file)
    if master_file in segment_files:
        segment_files.remove(master_file)
    return segment_files

# Get table list to analyze
def get_tables():
    con = DB(dbname = vDatabase)
    tables = con.get_tables()
    con.close()
    return tables

# To get count of completed backup_files
counter = Value('i', 0)
total_segment_files = len(get_segment_files())


def init(args):
    ''' store the counter for later use '''
    global counter
    counter = args

# Function to run analyze

def run_analyze(table):
    global counter
    con = DB(dbname = vDatabase)
    con.query("analyze %s" %table)
    con.close()
    with counter.get_lock():
        counter.value += 1
    if counter.value % 50 == 0 or counter.value == len(get_tables()):
        logger.info("analyze status: completed " + str(counter.value) + " out of " + str(len(get_tables())) + " tables or partitions ")

# Function to run segment backup_files
def run_segment_files(segment_file):
    global counter
    os.popen('psql %s -f %s -h %s >> /home/gpadmin/gpAdminLogs/parallel_restore_%s_%s.log 2>> /home/gpadmin/gpAdminLogs/parallel_restore_%s_%s.error' %(vDatabase, segment_file, vHost, vDump_key, vDate, vDump_key, vDate))
    with counter.get_lock():
        counter.value += 1
    logger.info(str(counter.value) + " files completed out of " + str(total_segment_files) + " files")
    # if counter.value % (vProcesses * 2) == 0:
    #     sendmail("Restore status: " + str(counter.value) + " files completed out of " + str(total_segment_files) + " files")



# Forking new #n processes for run_segment_files() Function
logger.info("Running segment file restore")
pool = Pool(initializer=init, initargs=(counter, ), processes=vProcesses)
pool.map(run_segment_files, get_segment_files())
pool.close()  # worker processes will terminate when all work already assigned has completed.
pool.join()  # to wait for the worker processes to terminate.

# Running set schema and set val statements
schema_path_set_val = open('/tmp/schema_path_set_val_%s.sql' %vDump_key,'a')
for line in open(master_file,'r'):
    if 'SET search_path' in line or 'SELECT pg_catalog.setval' in line:
        schema_path_set_val.write(line)


# Running post_data file
post_data_file = master_file + '_post_data'
run_schema_path_set_val = "psql %s -h %s -f /tmp/schema_path_set_val_%s.sql > /home/gpadmin/gpAdminLogs/parallel_restore_schema_path_set_val_%s.log" %(vDatabase, vHost, vDump_key, vDump_key)
run_post_data_file = "psql %s -h %s -f %s > /home/gpadmin/gpAdminLogs/parallel_restore_post_data_%s.log" %(vDatabase, vHost, post_data_file, vDump_key)

if os.path.isfile('/tmp/schema_path_set_val_%s.sql' %vDump_key):
    logger.info("Running schema_path_set_val")
    os.popen(run_schema_path_set_val)
else:
    logger.info("schema_path_set_val file doesn't exists")

if os.path.isfile(post_data_file):
    logger.info("Running post_data file")
    os.popen(run_post_data_file)
else:
    logger.info("Post data file doesn't exists")
logger.info("Restore completed")

if not options.noanalyze:
#     #sendmail("""
#                 Restore status: completed.\n
#                 Please review the log file in ~/gpAdminLogs directory (recommended)\n
#                 Running analyze:
#                 """)
#     logger.info("Running analyze on " + str(len(get_tables())) + " tables or partitions")
#     pool = Pool(initializer=init, initargs=(counter, ), processes=vProcesses)
#     pool.map(run_analyze, get_tables())
#     pool.close()  # worker processes will terminate when all work already assigned has completed.
#     pool.join()  # to wait for the worker processes to terminate.
#     sendmail("Analyze status: completed")
# else:
#     sendmail("""
#                 Restore status: completed.\n
#                 Analyze is skipped by request; database performance may be adversely impacted until analyze is done.\n
#                 Please review the log file in ~/gpAdminLogs directory (recommended)""")
    logger.warning("---------------------------------------------------------------------------------------------------")
    logger.warning("Analyze bypassed on request; database performance may be adversely impacted until analyze is done.")
    logger.warning("Please review the log file in ~/gpAdminLogs directory (recommended)")
    logger.warning("---------------------------------------------------------------------------------------------------")
