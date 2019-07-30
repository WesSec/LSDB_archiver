## **LSDB Scraper!**
This tool helps you to archive livesets from LSDB!

### **Disclaimer**
This is some hacky script i quickly wrote, it comes with absolutely no warranty or whatsoever, it works or it doesn't.
You can try to open an issue on github   
  

###**How does this work:**
1. Install the software
2. Use the software
3. ????
4. Profit, and some saved livesets

### **Installation instructions**
The obvious:  
`git clone this repo`  
`pip3 install -r requirements.txt`  
Make sure ffmpeg is installed, otherwise:  
`sudo apt install ffmpeg`

### **Usage**  
Run `python3 main.py` with the desired arguments, -i or -l is required:  
`-i [SET ID]`  
`-l [LIST WITH SET ID'S, a .txt file with each ID on a new line`  
`-o [OUTPUT LOCATION WITHOUT THE LAST SLASH, eg: /home/user/livesets]`

you can set force_mp3 to true in the config.ini file. This way the software tries to convert the audio file to mp3 (when it's downloaded in m4a or something), no guarantees tho.

