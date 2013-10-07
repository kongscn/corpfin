import csv
import os


def rec2csv( recs, file, mode='w', with_header=True):
    file_exist = False
    if os.access(file,os.F_OK):
        file_exist = True
    writer=csv.writer(open(file, mode, newline=''))
    if with_header:
        if mode == 'w' or (not file_exist):
            writer.writerow(recs.dtype.names)
    writer.writerows(recs)
