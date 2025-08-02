import os
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog
from mutagen.mp3 import MP3
from pygame import mixer

# Initialize mixer
mixer.init()

# Root window setup
root = Tk()
root.title("Melody Mood Music Player")
root.geometry("900x500")

# Global variables
playlist = []
paused = False
muted = False

# Define mood folders (update these paths as needed)
MOOD_FOLDERS = {
    "Happy": "moods/happy",
    "Sad": "moods/sad",
    "Energetic": "moods/energetic",
    "Relaxing": "moods/relaxing"
}

# Notification area
notification_label = Label(root, text="Welcome to Melody Mood Player!", font=("Arial", 12), bg="#000000", fg="white")
notification_label.pack(fill=X, pady=5)

def show_notification(message):
    notification_label.config(text=message)

def load_mood_playlist():
    global playlist
    playlistbox.delete(0, END)
    playlist = []
    mood = mood_choice.get()
    folder = MOOD_FOLDERS.get(mood)
    if folder and os.path.exists(folder):
        # Only add mp3 and wav files to the playlist
        for file in os.listdir(folder):
            if file.lower().endswith((".mp3", ".wav")):
                full_path = os.path.join(folder, file)
                playlist.append(full_path)
                playlistbox.insert(END, file)
        if playlist:
            show_notification(f"Loaded {len(playlist)} {mood} songs!")
        else:
            show_notification(f"No songs found for {mood}.")
    else:
        show_notification(f"Folder for mood '{mood}' not found!")

def browse_file():
    """Allows user to add songs manually to the current playlist."""
    global playlist
    file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file_paths:
        for file_path in file_paths:
            # Append full path to playlist and display only the filename
            playlist.append(file_path)
            playlistbox.insert(END, os.path.basename(file_path))
        show_notification(f"Added {len(file_paths)} song(s) manually.")

def play_music():
    global paused
    if paused:
        mixer.music.unpause()
        show_notification("Music Resumed")
        paused = False
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            if not selected_song:
                show_notification("No song selected!")
                return
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()
            show_details(play_it)
            show_notification(f"Playing - {os.path.basename(play_it)}")
        except Exception as e:
            show_notification(f"Error: {str(e)}")

def stop_music():
    mixer.music.stop()
    show_notification("Music Stopped")

def pause_music():
    global paused
    paused = True
    mixer.music.pause()
    show_notification("Music Paused")

def rewind_music():
    play_music()
    show_notification("Music Rewinded")

def mute_music():
    global muted
    if muted:
        mixer.music.set_volume(0.7)
        volume_slider.set(70)
        mute_btn.config(text="Mute")
        show_notification("Volume Unmuted")
        muted = False
    else:
        mixer.music.set_volume(0)
        volume_slider.set(0)
        mute_btn.config(text="Unmute")
        show_notification("Volume Muted")
        muted = True

def set_volume(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    show_notification(f"Volume: {int(val)}%")

def del_song():
    selected_song = playlistbox.curselection()
    if not selected_song:
        show_notification("No song selected to delete!")
        return
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)

def show_details(play_song):
    file_data = os.path.splitext(play_song)
    if file_data[1].lower() == ".mp3":
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    mins, secs = divmod(total_length, 60)
    timeformat = "{:02d}:{:02d}".format(int(mins), int(secs))
    length_label.config(text=f"Total Length: {timeformat}")

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()

def start_count(t):
    global paused
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            timeformat = "{:02d}:{:02d}".format(int(mins), int(secs))
            current_time_label.config(text=f"Current Time: {timeformat}")
            time.sleep(1)
            current_time += 1

# UI Elements

# Mood selection frame
mood_frame = Frame(root, bg="#2c3e50", relief=RIDGE, bd=5)
mood_frame.pack(pady=10)
mood_label = Label(mood_frame, text="Select Mood:", font=("Arial", 12), bg="#2c3e50", fg="white")
mood_label.pack(side=LEFT, padx=5)
mood_choice = ttk.Combobox(mood_frame, values=list(MOOD_FOLDERS.keys()), font=("Arial", 12), state="readonly")
mood_choice.current(0)
mood_choice.pack(side=LEFT, padx=5)
load_mood_btn = Button(mood_frame, text="Load Mood Playlist", font=("Arial", 10), bg="#1abc9c", fg="white", command=load_mood_playlist)
load_mood_btn.pack(side=LEFT, padx=5)

# Add song manually button
add_song_btn = Button(mood_frame, text="Add Song", font=("Arial", 10), bg="#1abc9c", fg="white", command=browse_file)
add_song_btn.pack(side=LEFT, padx=5)

# Left frame for playlist
left_frame = Frame(root, bg="#2c3e50", relief=RIDGE, bd=5)
left_frame.pack(side=LEFT, padx=30, pady=30)

playlistbox = Listbox(left_frame, bg="#34495e", fg="white", font=("Arial", 12), width=30, height=15, selectbackground="#1abc9c")
playlistbox.pack()

del_btn = Button(left_frame, text="- Del", font=("Arial", 10), bg="#e74c3c", fg="white", command=del_song)
del_btn.pack(pady=5)

# Right frame for controls and song details
right_frame = Frame(root, bg="#2c3e50", relief=RIDGE, bd=5)
right_frame.pack(padx=30, pady=30)

top_frame = Frame(right_frame, bg="#2c3e50")
top_frame.pack()

length_label = Label(top_frame, text="Total Length: --:--", bg="#2c3e50", fg="white", font=("Arial", 12))
length_label.pack(pady=5)

current_time_label = Label(top_frame, text="Current Time: --:--", bg="#2c3e50", fg="white", font=("Arial", 12))
current_time_label.pack(pady=5)

middle_frame = Frame(right_frame, bg="#2c3e50")
middle_frame.pack(pady=20)

play_btn = Button(middle_frame, text="Play", font=("Arial", 10), bg="#1abc9c", fg="white", command=play_music, width=10)
play_btn.grid(row=0, column=0, padx=10)

stop_btn = Button(middle_frame, text="Stop", font=("Arial", 10), bg="#e74c3c", fg="white", command=stop_music, width=10)
stop_btn.grid(row=0, column=1, padx=10)

pause_btn = Button(middle_frame, text="Pause", font=("Arial", 10), bg="#f39c12", fg="white", command=pause_music, width=10)
pause_btn.grid(row=0, column=2, padx=10)

bottom_frame = Frame(right_frame, bg="#2c3e50")
bottom_frame.pack()

rewind_btn = Button(bottom_frame, text="Rewind", font=("Arial", 10), bg="#9b59b6", fg="white", command=rewind_music, width=10)
rewind_btn.grid(row=0, column=0, padx=10)

mute_btn = Button(bottom_frame, text="Mute", font=("Arial", 10), bg="#3498db", fg="white", command=mute_music, width=10)
mute_btn.grid(row=0, column=1, padx=10)

volume_slider = Scale(bottom_frame, from_=0, to=100, orient=HORIZONTAL, command=set_volume, bg="#34495e", fg="white", font=("Arial", 10), length=200)
volume_slider.set(70)
volume_slider.grid(row=0, column=2, padx=20)

root.mainloop()
