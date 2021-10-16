import streamlit as st
from datetime import datetime
import os
from PIL import Image

def get_usable_image_dirs(base_dir):

    # list all files inside the base_dir
    files_list = os.listdir(base_dir)
    # isolate only the usably files that contain a specific keyword
    usable_files_list = [file_dir for file_dir in files_list if 'node_size__in' in file_dir]

    # isolate dates from filtered filenames
    datetimes_list = []
    datetime_to_file_dir_dict = {}

    for i, file_dir in enumerate(usable_files_list):
        temp_datetime = datetime.strptime(file_dir.split('_node')[0], '%d_%m_%Y')
        datetimes_list.append(temp_datetime)
        # datetime_to_file_dir_dict[temp_datetime] = base_dir+'/'+file_dir
        datetime_to_file_dir_dict[temp_datetime] = Image.open(base_dir+'/'+file_dir)
    datetimes_list.sort()
    return datetimes_list, datetime_to_file_dir_dict

def show():

    datetimes_list, datetime_to_file_dir_dict = get_usable_image_dirs('../images')

    image_placeholder = st.empty()

    selected_date = st.select_slider(
        "When do you start?",
        options=datetimes_list)

    image_placeholder.image(datetime_to_file_dir_dict[selected_date])

if __name__ == "__main__":
    show()