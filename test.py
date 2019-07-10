from __future__ import print_function
from multiprocessing import Process
import os

#
#
# def info(title):
#     print(title)
#     print('module name:', __name__)
#     if hasattr(os, 'getppid'):  # only available on Unix
#         print('parent process:', os.getppid())
#     print('process id:', os.getpid())
#
#
# def f(name):
#     print('f stated')
#     n=0
#     for n in range(10000000):
#         n=n+1
#     print('f exiting with %s'%n)
#     return 0
#
#
# if __name__ == '__main__':
#
#     p = Process(target=f, args=('bob',))
#     p.start()
#
#     info('main line')
#     p.join()
#     print('after join')

path = "AIS_PROJ/media/"
from os import listdir
import os
from pprint import pprint
from os.path import isfile, join
import json
import pprint
# onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
# # pprint(onlyfiles)
# for file in onlyfiles:
#     var = os.path.splitext(file)[0]
#     print(var)
# from events.views import s3
#
#
# s3.Bucket('ais-django').download_file('img.jpg', '/Events/Admin Project/DSC_0198.jpg')

str_data="""{ "id": 1, "timeSlots":[{"startTime":"13:36:57","endTime": "15:36:58"},{"id":2,"startTime":"09:36:57","endTime":"10:36:58"}],"date": "2018-12-04"},{"id": 2,"timeSlots": [ {"id": 2, "startTime": "09:36:57","endTime": "10:36:58" }], "date": "2018-12-05"}"""
json_data=json.loads(str_data)
pprint.pprint(json_data)