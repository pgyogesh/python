from multiprocessing import Pool
import multiprocessing
import os
import sys
import time

def segment_files(directory):
    segment_files = []
    for file in os.listdir(directory):
        segment_files.append(file)
    return segment_files

def run_segment_files(segment_file):
    print(segment_file)
    os.popen('psql -f %s > %s.log' %(segment_file,segment_file))

pool = Pool(processes=5)
pool.map(run_segment_files, segment_files('.'))
