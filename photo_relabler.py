from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk
import os
from collections import OrderedDict
from eye_patient_sorter import EyePhotoPatientSorter

# for debugging
# import pdb
# pdb.set_trace()

class PhotoReLabeler:
    """  
    Gui that serves batches of photos from chosen directory allowing user to choose the best
    quality photo and rename it using a id tag in a photo assumed to be in the batch.  

    Purpose: Create a well formatted corpus of eye photos for classification  
    """
    def __init__(self, master):
        self.master = master
        self.current_window = None
        self.current_folder = None
        self.current_save_folder = StringVar()
        self.working_dir = StringVar()
        self.thumbnail_size = (300,200)
        master.title("Photo Corpus Editor")

        # The default function is selecting and renaming
        self.active_function = IntVar()
        self.active_function.set(1) # initialize
        self.FUNCTIONS = {
            1:"Rename Files",
            2:"Segment and Tag Images"
            }
 
        self.main_instructions = Message(master, text="Select the directory to process: ")
        self.main_instructions.pack(anchor="n")
        Button(master, text="browse folders", command=self.askdirectory).pack()

        dir_disp = Frame(master)
        Label(dir_disp, text="Working Directory:", width=20).grid(row=0,column=0)
        Message(master,  textvariable=self.working_dir,width=100).grid(row=0,column=1)
        dir_disp.pack()


        for num in self.FUNCTIONS.keys():
            b = Radiobutton(master, text=self.FUNCTIONS[num],
                            variable=self.active_function, value=num)
            b.pack(anchor=W)

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def askdirectory(self):
        dirname = tkFileDialog.askdirectory() 
        if dirname == "/":
            return
        self.working_dir.set(dirname)

        # f_name = self.FUNCTIONS[self.active_function.get()].replace(" ", "_")
        # if self.active_function.get() == 1:
        #     save_dir = dirname + "_processed_" + f_name +"/"
        #     try: 
        #         os.mkdir(save_dir)
        #     except: 
        #         print("Folder Exists")
        #     self.current_save_folder = save_dir 

        # dirname += "/"
        # self.current_save_folder = dirname
        # self.rename_files(dirname)

    def rename_files(self, folder):   
        """ 
        calls process_next_batch so that the user can begin renaming the files in the chosen 
        directory. 

         ARGS:
            folder: string containing the absolute path of the directory to be processed
        """
        self.current_folder = folder
        self.photo_sorter = EyePhotoPatientSorter(folder)
        self.process_next_unlabeled_batch()

    def process_next_unlabeled_batch(self):     
        # If there are no more photos, return so that user can choose another directory. 
        if not self.photo_sorter.has_more_photos:
            notice = Toplevel()
            notice.title("Folder processesd")
            Message(notice, text="Congratulations, you renamed all the photos in this directory").pack()
            Button(notice, text="Give me more", command=notice.destroy).pack()
            Button(notice, text="I'm done", command=self.master.quit).pack()
            return

        # If we got here by skipping a batch, make sure to close the previous window
        if self.current_window is not None:
            self.current_window.destroy()
        self.current_window = Toplevel()
        self.current_window.title("Relabeling photos in " + self.current_folder)
        picture_frame = Frame(self.current_window)

        Message(self.current_window, text = "Select the best image, and enter the " +
                          "numberical ID you read off of the photo of " +
                          "the id tag.").pack()
        id_num = StringVar()
        Entry(self.current_window, text="Enter the number on the ID tag: ", textvariable=id_num).pack()

        # Get batch of photos and display them 
       
        self.batch = OrderedDict.fromkeys(self.photo_sorter.get_next_patient_filenames())
        COL = 0
        ROW = 0
        for f in self.batch.keys(): 
            orig = Image.open(f)
            im_small = Image.open(f)
            im_small.thumbnail(self.thumbnail_size)
            disp_photo = ImageTk.PhotoImage(im_small)
            photo = Button(picture_frame, image=disp_photo, 
                           command=lambda im=orig: self.save_image(id_num.get(), im))
            photo.im = disp_photo
            photo.grid(row=ROW, column=COL)
            # make sure that rows are only 3 images wide
            COL += 1
            if COL > 2:
                ROW += 1
                COL = 0

            picture_frame.pack()

        Button(self.current_window, text="Close", command=self.current_window.destroy).pack()
        Button(self.current_window, text="Next Batch", command=self.process_next_unlabeled_batch).pack()

    

    def save_image(self,id_num, im):
        if not id_num.isdigit():
            warning = Toplevel()
            warning.title("Could not understand input")
            Message(warning, text="WARNING: Id number has to be digits only").pack()
            return 

        save_name = self.current_save_folder.get() + str(id_num) + ".JPG"
        im.save(save_name)
        self.current_window.destroy()
        self.process_next_unlabeled_batch()
        return True






root = Tk()
my_gui = PhotoReLabeler(root)
root.mainloop()