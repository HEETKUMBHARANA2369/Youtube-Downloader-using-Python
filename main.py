from customtkinter import *
from PIL import Image
import requests
import json
import threading
import tkinter.messagebox as messagebox
import os

base_window = CTk()
base_window.title("Youtube Video Downloader")
base_window.geometry("500x450")  # Increased height to accommodate progress bar
base_window._set_appearance_mode("dark")

# Key bindings
def exit(key):
    base_window.destroy()
base_window.bind("<Escape>", exit)

# Create a global variable to store the list of (quality, url) tuples
quality_list = []

# Submit button binding
def Search():
    print("Search Button pressed")

    # Define the video URL
    video_url = entry_box.get()

    # Send GET request to the API
    response = requests.get(f"https://lokiai.netlify.app/.netlify/functions/yt-info?url={video_url}")

    # Check if the request was successful
    if response.status_code == 200:
        global video_title
        # Parse the response JSON
        video_data = response.json()
        # Extract the title from the nested "response" dictionary
        video_title = video_data.get("response").get("title", "Title not available")
        if len(video_title) <= 50:
            title_label_font.configure(size=15)
        else:
            title_label_font.configure(size=10)
        title_label.configure(text=f"TITLE: {video_title}")

        global quality_list
        quality_list.clear()  # Clear previous qualities

        formats = video_data.get("response").get("formats")
        for item in formats:
            quality = item.get("quality")  # Assuming quality key holds the quality name
            vid_type = item.get("type")
            print(vid_type)  # Assuming quality key holds the quality name
            url = item.get("url")
            if quality and url:
                quality_list.append((quality, url))  # Append a tuple (quality, url) to the list
        # print(quality_list) to see the quality list, uncomment this 
        
        dropdown.configure(values=[q[0] for q in quality_list])  # display qualities in dropdown

    else:
        print("Error retrieving video info:", response.status_code)

# Function to be run in a separate thread for video download
def download():
    selected_quality = dropdown.get()
    print(f"User selected {selected_quality}")

    if selected_quality == "Qualities":
        print("Please select a valid quality")
        messagebox.showerror("Error", "Please select a valid quality")
        return

    # Find the first matching quality URL
    video_url = next((url for q, url in quality_list if q == selected_quality), None)

    if not video_url:
        print("Selected quality URL not found.")
        messagebox.showerror("Error", "Selected quality URL not found")
        return

    # Download the video
    download_response = requests.get(video_url, stream=True)
    total_size = int(download_response.headers.get('content-length', 0))
    block_size = 4096  # 1 Kibibyte
    downloaded = 0

    with open(f'{video_title}.mp4', 'wb') as video_file:
        for data in download_response.iter_content(block_size):
            size = video_file.write(data)
            downloaded += size
            progress = int(50 * downloaded / total_size)
            base_window.after(0, progress_bar.set, downloaded / total_size)

    print("Video downloaded successfully!")
    base_window.after(0, progress_bar.set, 1.0)  # Ensure progress bar is full
    messagebox.showinfo("Success", "Video downloaded successfully!")

# Function to start download in a separate thread
def start_download_thread():
    progress_bar.set(0)  # Reset progress bar
    threading.Thread(target=download).start()

# Making font objects
Title_font = CTkFont(family="Poppins Bold", size=24)
sub_title_font = CTkFont(family="Poppins", size=14)
input_label_font = CTkFont(family="Poppins Medium", size=12)
download_button_font = CTkFont(family="Poppins SemiBold", size=14)
title_label_font = CTkFont(family="Poppins", size=15)

# Configuring rows and columns as per grid's weight
base_window.grid_columnconfigure(3, weight=2)
base_window.grid_rowconfigure(8, weight=2)

# Creating title label
title_label = CTkLabel(master=base_window, text="Youtube Video Downloader", font=Title_font, text_color="#E0E0E0")
title_label.grid(row=1, column=3, sticky="nsew", pady=10)

# Setting subtitle
sub_title = CTkLabel(master=base_window, text="Fast and Efficient Youtube video downloader", font=sub_title_font, text_color="#E0E0E0")
sub_title.grid(row=2, column=3, sticky="nsew", pady=10)

# Input label and input box
input_label = CTkLabel(master=base_window, text="Paste your URL", font=input_label_font, text_color="#E0E0E0")
input_label.grid(row=3, column=3, sticky="nsew", pady=10)
entry_box = CTkEntry(master=base_window, width=350, border_width=0, font=("Arial", 14))
entry_box.grid(row=4, column=3, padx=10)

# Setting search Image
search_image = CTkImage(Image.open("find.ico"))  # Ensure the image path is correct
search_ico = CTkButton(master=base_window, image=search_image, text="", width=50, fg_color="#3D3D3D", command=Search, hover_color="#5D5D5D", corner_radius=25)
search_ico.grid(row=4, column=3, sticky="e", padx=10)

# Setting Download Button
download_button = CTkButton(master=base_window, text="Download", fg_color="#FF4C4C", command=start_download_thread, font=download_button_font)
download_button.grid(row=7, column=3, pady=10)

# Setting label for details for the video extracted from link
title_label = CTkLabel(master=base_window, text="", font=title_label_font)
title_label.grid(row=5, column=3)

# Dropdown for the qualities
dropdown = CTkOptionMenu(master=base_window, values=["Qualities"])  # It will be populated later
dropdown.grid(row=6, column=3)

# Progress Bar
progress_bar = CTkProgressBar(master=base_window, width=350, height=20)
progress_bar.grid(row=8, column=3, pady=10)
progress_bar.set(0)  # Initialize progress bar to 0

# Starting the app
base_window.mainloop()