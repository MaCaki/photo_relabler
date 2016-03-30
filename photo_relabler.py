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
        self.master.geometry("750x200")
        self.current_window = master
        self.current_save_folder = StringVar()
        self.working_dir = StringVar()
        self.thumbnail_size = (300,200)
        master.title("Photo Corpus Editor")

        Message(text="For use with eyelid photos.  Relabel and add meta data to photo files for data processing.",
            width=550, pady=5,relief=RIDGE,justify=LEFT).pack()

        self.active_function = IntVar()
        self.active_function.set(1) # initialize
        self.FUNCTIONS = {
            1:{"name":"Rename Files",
                "desc":"Displays batches of patient photos from the selected "
                        + "directory. Select the best quality sample and rename the file "
                        + "with the proper ID number displayed in the id tag.",
                "func": self.rename_files},
            2:{ "name": "Segment and Tag Images",
                "desc": "Segment out the eyelid region as well as select centroids "
                        + "of the lid and the follicles on the lid if present.",
                "func": self.tag_follicles}
            }

       

        directory_display = Frame(master)
        Button(directory_display, text="Select the directory to process", command=self.askdirectory).grid(row=0,column=0)
        Label(directory_display, text=" : ", width=10).grid(row=0,column=1)
        Message(directory_display,  textvariable=self.working_dir ,width=500,relief=RIDGE).grid(row=0,column=2)
        directory_display.pack()

       
        function_grid = Frame(master)
        Message(function_grid,  text="Select how you want to process this folder:",
            width=400,pady=5,justify=LEFT).grid(row=0,columnspan=2,sticky=W)
        for i,num in enumerate(self.FUNCTIONS.keys()):
            b = Radiobutton(function_grid, text=self.FUNCTIONS[num]["name"],
                            variable=self.active_function, value=num).grid(row=i+1,column=0,sticky=W)
            Message(function_grid, text=self.FUNCTIONS[num]["desc"], width=550).grid(row=i+1,column=1,sticky=W)
        function_grid.pack()

        Button(master, text="PROCESS", command=self.process_directory).pack()
       
        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()


    def askdirectory(self):
        dirname = tkFileDialog.askdirectory() 
        if dirname == "/":
            return
        self.working_dir.set(dirname)

    def process_directory(self):
        f = self.FUNCTIONS[self.active_function.get()]["func"]
        f()
 
     #--------    Tagging Images    --------#  
    def tag_follicles(self):
        self.photo_sorter = EyePhotoPatientSorter(self.working_dir.get(), sort=False)
        return 

    def display_next_image_for_tagging(self):

        self.current_window = Toplevel()

        orig = Image.open(image_file)
        disp_photo = ImageTk.PhotoImage(orig)
        image_canvas.create_image((0,0),image=disp_photo)
        image_canvas.im = disp_photo

        image_canvas.pack()
        Button(self.current_window, text="Close", command=self.current_window.destroy).pack()

    #--------    Renaming Files    --------#  
    def rename_files(self):   
        """ 
        calls process_next_batch so that the user can begin renaming the files in the chosen 
        directory. 

         ARGS:
            folder: string containing the absolute path of the directory to be processed
        """

        # Create the save dir: 
        self.current_save_folder.set(self.working_dir.get() + "/_renamed_/")
        try: 
            os.mkdir(self.current_save_folder.get())
        except: 
            print("Folder Exists")

        self.photo_sorter = EyePhotoPatientSorter(self.working_dir.get())
        self.process_next_unlabeled_batch()

    def process_next_unlabeled_batch(self):     
        # If there are no more photos, return so that user can choose another directory. 
        if not self.photo_sorter.has_more_photos:
            notice = Toplevel()
            notice.title("Folder processed")
            Message(notice, text="Congratulations, you renamed all the photos in this directory").pack()
            Button(notice, text="Continue Working", command=notice.destroy).pack()
            Button(notice, text="I'm done", command=self.master.quit).pack()
            return

        # If we got here by skipping a batch, make sure to close the previous window
        if self.current_window is not None:
            self.current_window.destroy()

        self.current_window = Toplevel()
        self.current_window.title("Relabeling photos in " + self.working_dir.get())
        

        Message(self.current_window, text = "Select the best image, and enter the " +
                          "numerical ID you read off of the photo of " +
                          "the id tag.").pack()
        id_num = StringVar()
        Entry(self.current_window, text="Enter the number on the ID tag: ", textvariable=id_num).pack()

        # Get batch of photos and display them 
        picture_frame = Frame(self.current_window)
        photo_batch = OrderedDict.fromkeys(self.photo_sorter.get_next_patient_filenames())
        # COL = 0
        # ROW = 0
        for i,f in enumerate(photo_batch.keys()): 
            orig = Image.open(f)
            im_small = Image.open(f)
            im_small.thumbnail(self.thumbnail_size)
            disp_photo = ImageTk.PhotoImage(im_small)
            photo = Button(picture_frame, image=disp_photo, 
                           command=lambda im=orig: self.save_image(id_num.get(), im))
            photo.im = disp_photo
            COL = i%3
            ROW = i/3

            photo.grid(row=ROW, column=COL)
            # make sure that rows are only 3 images wide
            # COL += 1
            # if COL > 2:
            #     ROW += 1
            #     COL = 0

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
     #--------   end Renaming Files    --------#  



root = Tk()
my_gui = PhotoReLabeler(root)
root.mainloop()