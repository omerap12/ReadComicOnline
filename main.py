#created by Omerap12

from tkinter import*
from tkinter import filedialog
from tkinter import messagebox
import os,re
import time
import requests
from threading import *

#global variables
global isDirectory
isDirectory = False
texture=""
global isFinished
isFinished = False

#threading: download files + initiate progress lable
def threading():
    t1 = Thread(target=initDownload)
    t1.start()
    if (isDirectory):
        t2 = Thread(target=loading)
        t2.start()


#progress lable, open new window with the lable
def loading():
    e.delete(0,END)
    newWindow = Toplevel(root)
    newWindow.title("Progress")
    progress_lable = Label(newWindow, text=texture)
    progress_lable.pack()
    time.sleep(2)
    popUp("Warning","using Threads: Please wait to complete download.")
    while True:
        if (isFinished):
            break
        time.sleep(2)
        progress_lable.configure(text=texture)
    newWindow.quit()

#getting path of directory
def getDirectory():
    global directoryPath
    directoryPath = filedialog.askdirectory()
    global isDirectory
    isDirectory = True

#getting page information using requests
def getFirstResponse(url):
    try:
        response = requests.get(url=url)
        global info
        info = response.content.decode('utf-8')
    except Exception as exe:
        print("Error")
        print(exe)
        exit(1)


#extracting links from the substring
def getLinks(pageInfo):
    pattern = 'lstImages.push\(\"(.*)\"'
    result = re.findall(pattern,pageInfo)
    return result

#start downloading images and updating status window
def downloadingImages(links,source,name):
    size = len(links)
    path = os.path.join(source,name)
    try:
        os.mkdir(path=path)
    except OSError as error:
        popUp("Error","Directory already exist or can't find directory")
        popUp("Error",error)
        exit(2)
    os.chdir(path=path)
    for index in range(size):
        global texture
        texture = "Downloaded file: " + str(index) + " out of " + str(size)
        image = requests.get(links[index])
        file = open("photo" + str(index) + ".jpg", "wb")
        file.write(image.content)
        file.close()
    popUp("Finished!","Finished downloading!")
    global isFinished
    isFinished = True
    time.sleep(1)

#getting the name of comic
def getNameOfManga(link):
    names = link.split("/")
    #name of comic
    return names[4]

#getting page source code
def getFirstResponse(link):
    response = requests.get(link)
    return response.content.decode('utf-8')


#start downloading process, checking valid output path
def initDownload():
    if (isDirectory == False):
        popUp("Error","Please choose directory first")
        return
    url = e.get()
    nameOfManga = getNameOfManga(link=url)
    links = getLinks(getFirstResponse(url))
    downloadingImages(links=links,source=directoryPath,name=nameOfManga)

#pop up function
def popUp(message1,message2):
    messagebox.showinfo(message1,message2)

def exit():
    root.quit()

#initiate screen
root = Tk()
root.geometry("350x200")
root.title("ReadComicOnlineDownloader")
e = Entry(root,width=45,borderwidth=5)
e.grid(row=0,column=0,columnspan=3,padx=10,pady=10)
goButton = Button(root,text="Download",bg='green',font=('Arial', 13 ),padx=40,pady=20,command=threading)
goButton.grid(row = 1,column=2)
directoryButton = Button(root,text="Choose directory",bg='yellow',font=('Arial', 13 ),padx=22,pady=20,command=getDirectory)
directoryButton.grid(row = 1,column=1)
exitButton = Button(root,text="Exit",bg='red',font=('Arial', 13 ),padx=40,pady=20,command=exit)
exitButton.grid(row=2,column=2,columnspan=2)
my_lable = Label(root, text="Created by Omerap12",font=('Helvetica', 13, 'bold'))
my_lable.grid(row=2, column=0,columnspan=2)
root.mainloop()