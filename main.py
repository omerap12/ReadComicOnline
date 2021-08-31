# created by Omerap12

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os, re
import time
import requests
from threading import *
import shutil

# global variables
global isDirectory
isDirectory = False
texture = ""
global isFinished
isFinished = False
global isMultipleFinished
isMultipleFinished = True


# threading: download files + initiate progress lable
# threading for single comic downloading
def threading():
    t1 = Thread(target=initDownload)
    t1.start()
    if (isDirectory):
        t2 = Thread(target=loading)
        t2.start()


# threading for multi-comic downloading
def threadingMultiple():
    t1 = Thread(target=initMultipleIssuesDownload)
    t1.start()
    if (isDirectory):
        t2 = Thread(target=loading)
        t2.start()


# progress lable, open new window with the lable
def loading():
    # clearing the entry
    e.delete(0, END)
    # open new window - progress bar
    newWindow = Toplevel(root)
    # window's name
    newWindow.title("Progress")
    # creating progress lable
    progress_lable = Label(newWindow, text=texture)
    progress_lable.pack()
    # waiting for 2 seconds (for requests , etc.)
    time.sleep(2)
    popUp("Warning", "using Threads: Please wait to complete download.")
    # updating progress bar
    while True:
        if (isFinished):
            break
        time.sleep(2)
        progress_lable.configure(text=texture)
    # if downloading is finished, close window
    newWindow.quit()


# getting path of directory
def getDirectory():
    # initiate global string variable
    global directoryPath
    # getting directory path
    directoryPath = filedialog.askdirectory()
    # set boolean variable to True
    global isDirectory
    isDirectory = True


# getting page information using requests
def getFirstResponse(url):
    # trying to get page content, using response
    try:
        response = requests.get(url=url)
        global info
        info = response.content.decode('utf-8')
    # if couldn't get page content exit
    except Exception as exe:
        print("Error")
        print(exe)
        exit(1)


# extracting links from the substring
def getLinks(pageInfo, pattern):
    # getting all result using regex
    result = re.findall(pattern, pageInfo)
    return result


# start downloading images and updating status window
def downloadingImages(links, source, name, isIssues, numberOfIssues, currentIsssue):
    # getting size of photos in comic-book page
    size = len(links)
    # getting path name
    path = os.path.join(source, name)
    # try to make new directory for the comic book
    try:
        os.mkdir(path=path)
    # if error, exit
    except OSError as error:
        popUp("Error", "Directory already exist or can't find directory")
        popUp("Error", error)
        exit(2)
    # changing directory to the desire directory
    os.chdir(path=path)
    # working on each photo
    for index in range(size):
        global texture
        # if user asked for single comic book, print progress of each photo
        if (isIssues == False):
            texture = "Downloaded file: " + str(index) + " out of " + str(size)
        # if user asked for entire title collection, print progress of each comic-book
        else:
            texture = "Downloading issue " + str(currentIsssue) + " out of " + str(numberOfIssues)
        # getting the image, writing in binary mode
        image = requests.get(links[index])
        padOutIndex = str(index).zfill(5)
        file = open("photo" + padOutIndex + ".jpg", "wb")
        # writing
        file.write(image.content)
        # close file
        file.close()
    # if finished all downloading , print and exit
    if isIssues == False or (isIssues == True and currentIsssue == numberOfIssues):
        popUp("Finished!", "Finished downloading!")
        global isFinished
        isFinished = True
        time.sleep(1)


# getting the name of comic
def getNameOfComics(link, isIssue):
    names = link.split("/")
    # name of comic
    # if user asked for entire title collection add name of issue to directory's name
    if isIssue:
        partOneOfName = names[4]
        partTwoOfName = names[5].split('?')[0]
        return partOneOfName + ' ' + partTwoOfName
    # if not stay name as is
    return names[4]


# getting page source code
def getFirstResponse(link):
    # getting page content (first time)
    response = requests.get(link)
    # return It's content
    return response.content.decode('utf-8')


# getting all comic-books links in the collection
def getMultipleIssuesLinks(link):
    # getting page content
    content = getFirstResponse(link)
    # return all links of the comic-books collection
    return getLinks(content, pattern="<a  href=\"(.*)\"")


# downloading all comic-books in the entire title collection
def initMultipleIssuesDownload():
    # if  user doesn't provide path, print error
    if (isDirectory == False):
        popUp("Error", "Please choose directory first")
        return
    # get the link of the page from entry
    url = e.get()
    # calling function to get all comic-books link
    links = getMultipleIssuesLinks(link=url)
    siteUrl = "https://readcomiconline.li"
    count = 1
    # iterate through comic books links and downloading each one
    for value in links:
        comicUrl = siteUrl + value
        nameOfComics = getNameOfComics(link=comicUrl, isIssue=True)
        photoUrls = getLinks(getFirstResponse(comicUrl), pattern='lstImages.push\(\"(.*)\"')
        downloadingImages(links=photoUrls, source=directoryPath, name=nameOfComics, isIssues=True,
                          numberOfIssues=len(links), currentIsssue=count)
        count += 1


# start downloading process of single comic-book, checking valid output path
def initDownload():
    # if  user doesn't provide path, print error
    if (isDirectory == False):
        popUp("Error", "Please choose directory first")
        return
    # get the link of the page from entry
    url = e.get()
    # getting name of comic-book
    nameOfComics = getNameOfComics(link=url, isIssue=False)
    # downloading process
    links = getLinks(getFirstResponse(url), pattern='lstImages.push\(\"(.*)\"')
    downloadingImages(links=links, source=directoryPath, name=nameOfComics, isIssues=False, numberOfIssues=0,
                      currentIsssue=0)


# function to convert issues into one comics-file
def createComic():
    # pop up message
    popUp("File location", "Pick folder of all comics")
    # file location window
    getDirectory()
    # saving path
    sourcePath = directoryPath
    # if user didn't choose folder, except error
    try:
        os.chdir(sourcePath)
    except OSError:
        return
    popUp("Working","Please wait.")
    # getting name of output folder
    nameOfOutPutFolder = getOutPutDirectoryName(sourcePath)
    # creating the folder
    os.mkdir(nameOfOutPutFolder)
    # saving the path to the folder
    outputPath = os.path.abspath(nameOfOutPutFolder)
    # init counter to zero
    count = 0
    # iterating through directories in main folder
    for dir in os.listdir(os.getcwd()):
        # saving their path
        correctInputPathDirectory = getCorrectInputPath(directory=dir)
        # iterating through the files in each folder
        for file in os.listdir(dir):
            #pad out
            padOutIndex = str(count).zfill(5)
            # initiate name
            name = "\\photo" + padOutIndex + ".jpg"
            # initiate path of photo
            correctInputPathFile = correctInputPathDirectory + '\\' + file
            # copy photo to the dest
            shutil.copy(correctInputPathFile, outputPath + name)
            # counter is up by one
            count += 1
    # converting directory to winrar file
    shutil.make_archive(nameOfOutPutFolder, "zip", outputPath)
    oldName = nameOfOutPutFolder + ".zip"
    newName = nameOfOutPutFolder + ".cbz"
    # changing to cbz format
    os.rename(oldName, newName)
    # finished pop up window
    popUp("Finished!", "Finished Convert All issues to one cbz format." + str(count) + " created.")


# funtion to get file path
def getCorrectInputPath(directory):
    original = os.path.abspath(directory)
    return (original)


# pop up function
def popUp(message1, message2):
    messagebox.showinfo(message1, message2)


# function to get the name of the directory
def getOutPutDirectoryName(source):
    path = source.split("/")
    return path[len(path) - 1]


# exit function
def exit():
    root.quit()


# initiate screen
root = Tk()
root.geometry("650x200")
root.title("ReadComicOnlineDownloader")
e = Entry(root, width=55)
e.grid(row=0, column=0, columnspan=3, padx=30, pady=10)
goButton = Button(root, text="Single Download", bg='pink', font=('Arial', 13), padx=40, pady=20, command=threading)
goButton.grid(row=1, column=2)
multipleButton = Button(root, text="Title Collection Download", bg='green', font=('Arial', 13), padx=40, pady=20,
                        command=threadingMultiple)
multipleButton.grid(row=1, column=3)
directoryButton = Button(root, text="Choose directory", bg='yellow', font=('Arial', 13), padx=22, pady=20,
                         command=getDirectory)
directoryButton.grid(row=1, column=1)
exitButton = Button(root, text="Exit", bg='red', font=('Arial', 13, 'bold'), padx=100, pady=20, command=exit)
exitButton.grid(row=2, column=2, columnspan=2)
createComic = Button(root, text="Create Comic", bg='white', font=('Arial', 13), padx=100, pady=20, command=createComic)
createComic.grid(row=2, column=1, columnspan=2)
my_lable = Label(root, text="Created by Omerap12", font=('Helvetica', 13, 'bold'))
my_lable.grid(row=3, column=0, columnspan=2)
root.mainloop()
