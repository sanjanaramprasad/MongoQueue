'''Lists processes which are bound to ip address
Format of the process will be as follows
port:<port number>,Process:<details of the path of the process>'''
import os,re
dic={}
def port():
	#Lists all processes and their corresponding port numbers. 
	#a finction pid() is called with details of the process's port numbers and protocol
	f=open("Problem2_Result.txt","w+")
	processoutput=os.popen("netstat -na | grep LISTEN").read()
	lines=processoutput.split("\n")
	#print(lines)
	for each in lines:
		if each:
			word=each.split()
			if(re.match("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\:[0-9]+",word[3])):
				#print(word[3])
				f.write(each)
				f.write("\n")
				port=word[3].split(":")[1]
				prot=word[0]
				#print(prot)
				#print(port)
				pid(str(prot),str(port))
def pid(prot,port):
	#lists the pid of the process
	#Using the pid another function name_of_program is called
	#The function is called to find out the name of the process using port numbers
	execution ="lsof -i "+prot+":"+port
	output=os.popen(str(execution)).read()
	if output:
		result=output.split("\n")[1]
		#print("RESULT",result)
		pid=result.split()[1]
		#print("PID",pid)
		name_of_program(str(pid),port)

def name_of_program(pid,port):
	#lists out the corresponding process name
	#the process and their respoective names are stored in a dictionary
	command="ps -eaf | grep "+pid
	output_name=os.popen(str(command)).read()
	if output_name:
		#print("FINAL",output_name)
		processes=output_name.split("\n")
		#print("PROCESSES",processes)
		for each in processes:
			#print("CHECK",each)
			if each:
				lister=each.split()
				if str(lister[1]) == pid:
					name=re.split("[0-9]+\:[0-9]+\:[0-9]+",each)[1]
					#print("NAME:",name)
					global dic
					dic[port]=name
	#print(dic)
	
def print_final():
	#prints port number and name of the process, according to what is stored in the dictionary
	for each in dic:
		final="PORT: "+each+" ,"+"PROCESS: "+dic[each]
		print final


port()
print_final()

