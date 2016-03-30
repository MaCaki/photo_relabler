from PIL import Image, ImageTk
import os
from collections import OrderedDict


class EyePhotoPatientSorter:
    """ 
    Class to hold the logic and current state of the batch sorter of the directory to be 
    inspected and renamed.  Assumes that patients are separated by images of white id tags
    """

    def __init__(self, directory):
        self.file_names= iter([directory + "/" + f for f in os.listdir(directory) if f.endswith(".JPG") or f.endswith(".jpg")])
        self.sort = True
        self.white_thresh = 0.25  # from rough experiment
        self.has_more_photos = True
        self.thumbnail_size = (600,400)
        self.current_photo = self.file_names.next()

    def get_next_photo(self):
        return 0

    def get_next_patient_filenames(self):
        if not self.has_more_photos:
            print("directory exhausted") 
            return 0

        patient_photos = []
        try:
            while(self.is_id_tag_photo(self.current_photo)):
                patient_photos += [self.current_photo]
                self.current_photo = self.file_names.next()

            while(not self.is_id_tag_photo(self.current_photo)):
                patient_photos += [self.current_photo]
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