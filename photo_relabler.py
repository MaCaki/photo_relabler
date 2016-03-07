from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk
import os
from collections import OrderedDict

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
        self.current_save_folder = None
        self.thumbnail_size = (300,200)
        master.title("A simple GUI")
        button_frame = Frame(master, width=1000, height=1000)
 
        self.main_instructions = Message(master, text="Select the directory to work in: ")
        self.main_instructions.pack(anchor="n")
        Button(master, text="browse folders", command=self.askdirectory).pack()

        FUNCTIONS = [
        ("Relabel", 1),
        ("Segment Eyelid", 2),
        ("Select Follicles", 3),
        ("Select Centroid", 4)
        ]

        processing_functions = {}

        active_function = IntVar()
        active_function.set(1) # initialize

        for function, num in FUNCTIONS:
            b = Radiobutton(master, text=function,
                            variable=active_function, value=num)
            b.pack(anchor=W)

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()



    def process_folder(self, folder):   
        """ 
        calls process_next_batch so that the user can begin renaming the files in the chosen 
        directory. 

         ARGS:
            folder: string containing the absolute path of the directory to be processed
        """
        self.current_folder = folder
        self.photo_sorter = EyePhotoPatientSorter(folder)
        self.process_next_batch()


    def process_next_batch(self):     
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
        Button(self.current_window, text="Next Batch", command=self.process_next_batch).pack()

    

    def save_image(self,id_num, im):
        if not id_num.isdigit():
            warning = Toplevel()
            warning.title("Could not understand input")
            Message(warning, text="WARNING: Id number has to be digits only").pack()
            return 

        save_name = self.current_save_folder + str(id_num) + ".JPG"
        im.save(save_name)
        self.current_window.destroy()
        self.process_next_batch()
        return True

    def askdirectory(self):
        dirname = tkFileDialog.askdirectory() 
        if dirname == "/":
            return

        save_dir = dirname + "_renamed/"
        try: 
            os.mkdir(save_dir)
        except: 
            print("Folder Exists")
        dirname += "/"
        self.current_save_folder = save_dir 
        self.process_folder(dirname)



class EyePhotoPatientSorter:
    """ 
    Class to hold the logic and current state of the batch sorter of the directory to be 
    inspected and renamed.  Assumes that patients are separated by images of white id tags
    """

    def __init__(self, directory):
        self.file_names= iter([directory + f for f in os.listdir(directory) if f.endswith(".JPG")])
        self.white_thresh = 0.25  # from rough experiment
        self.has_more_photos = True
        self.thumbnail_size = (600,400)
        self.current_photo = self.file_names.next()

    def get_next_patient_filenames(self):
        if not self.has_more_photos:
            print("directory exhausted") 
            return 0

        patient_photos = []
        try:
            while(self.is_id_tag_photo(self.current_photo)):
                patient_photos.append(self.current_photo)
                self.current_photo = self.file_names.next()

            while(not self.is_id_tag_photo(self.current_photo)):
                patient_photos.append(self.current_photo)
                self.current_photo = self.file_names.next()
        except StopIteration as e: 
            self.has_more_photos = False    

        return patient_photos



    """ Returns true if the number of "white" pixels in the thumbnail image is over
    1500.  Perhaps this should be changed to a percentage so that it can handle any size image"""           
    def is_id_tag_photo(self, file_name):
        im = Image.open(file_name)
        im.thumbnail(self.thumbnail_size)
        pixels = list(im.getdata())
        n = len(pixels)
        num_whites = sum([1 for x in pixels if (x[0]>150 and x[1]>150 and x[2]>150)])
        percent_white = float(num_whites)/n
        if (percent_white > self.white_thresh):
            return True
        else: 
            return False



root = Tk()
my_gui = PhotoReLabeler(root)
root.mainloop()