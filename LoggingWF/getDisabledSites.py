import pandas as pd
from Mail.mail import *
def get_logs(location): #Get all lines form the log file and store into a list 
    lines = []
    with open(location) as f:
        # global lines
        lines = f.readlines()
        # print(lines[0:2])
        # for()
    return lines
def get_sources_that_are_not_working(lines): #Go through the log to find the sources that are not working 
    sources = []
    for val,i in enumerate(lines):
        if(i.find("not working")!=-1):
            sources.append(i.split(" ")[0])
        elif(i.find("Empty datframe") != -1):
            sources.append(i.split(":")[0])
        if(i.find("DataFrame") != -1):
            sources.append(lines[val-2])
        if(len(i.split()) == 1):
            sources.append(i)
    return list(set(sources))
def remove_unwanted_junk_from_sources(sources): #Remove unwanted lines tracked in sources failed list 
    res = []
    for i in sources:
        if(len(i.split()) == 1):
            res.append(i.split("\n")[0])
    return res
def remove_duplicates_from_log():
    # data1 = []
    with open("logs.txt","r") as f:
        data = set(f.read().split("\n"))
    with open("logs1.txt","r") as f:
        data1 = set(f.read().split("\n"))
    res = data.union(data1)
    with open("logs.txt","w") as f:
        for i in res:
            f.write(i+"\n")
    sendemail("sharikavallambatlapes@gmail.com","vishwajeethogale307@gmail.com","Daily run : Automated log report","logs.txt")
    
    
def run_feature4(file):
    lines = get_logs(file)
    sources = get_sources_that_are_not_working(lines)
    final_sources = remove_unwanted_junk_from_sources(sources)
    remove_duplicates_from_log()
    return final_sources
if __name__ =="__main__":
    remove_duplicates_from_log()