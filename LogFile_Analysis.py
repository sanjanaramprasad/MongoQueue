import time,threading
from threading import*
import os,re
import getopt
import sys
import time
from itertools import islice
#no_of_lines_read=0
n=100000
filename=''
regex=[]
dic={}
fo=open("Result.txt","w")
def main(argv):
   if(len(argv) == 0):
      print 'test.py -f <input file> -r <regEx> -r <regEx>...'
      sys.exit(2)
   else:
      try:
         opts,args=getopt.getopt(argv,"f:r:",["regEx="])
      except getopt.GetoptError:
         print 'test.py -f <input file> -r <regEx> -r <regEx>...'
         sys.exit(2)
      for opt, arg in opts:
         if opt == '-f':
            global filename
            filename=arg
         elif opt in ("-r"):
            global regex
            regex.append(arg)

      print("FILE BEING WATCHED :",filename)

class myThread(threading.Thread):
   def __init__(self,filename,dic):
      threading.Thread.__init__(self)
      self.filename=filename
      self.dic=dic
   def run(self):
      no_of_lines_read=0
      modified=os.stat(filename).st_mtime
      lastModified=modified
      while True:
       time.sleep(1)
       lastModified=os.stat(filename).st_mtime
       if(modified != lastModified):
         with open(filename) as f:
            next_lines=list(islice(f,no_of_lines_read,n))
            for each in next_lines:
               no_of_lines_read=no_of_lines_read+1
               #print ("files line",each)
               for reg in regex:
                  if(re.search(reg,each)):
                     if not reg in dic:
                        #print"lsl"
                        dic[reg]=1
                     else:
                        #print"kak"
                        dic[reg]+=1
      modified=lastModified
   
   def suicide(self):
      raise RuntimeError('Stop has been called')

class myThread2(threading.Thread):
   def __init__(self,dic,fo):
      threading.Thread.__init__(self)
      self.dic=dic
   def run(self):
      #print("here")
      if len(dic)!= 0:
         print("--------------------------------------------------")
         print("Count of all the matched patterns are : \n")
         for each in dic:
            print(each +":" +str(dic[each]))
            print("--------------------------------------------------")
   def suicide(self):
      raise RuntimeError('Stop has been called')


if __name__== '__main__':
   main(sys.argv[1:])
   threadLock = threading.Lock()
   threads = []
   thread1 = myThread(filename,dic)
   thread2 = myThread2(dic,fo)
   thread2.start()
   threads.append(thread1)
   threads.append(thread2)
   thread1.start()
   while True:
      time.sleep(15)
      thread2.run()

