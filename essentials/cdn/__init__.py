import requests, os

def CDN_Download(filedir, SERVER="https://cdn.mknxgn.pro/datastore/", is_dir=False):
    """
    MkNxGn CDN - CONTENT DELIVERY NETWORK
    
    This function is used for downloading files from the
    MkNxGn CDN. You will most likely need this for downloading tutorials.

    filedir - Path to the file/folder you with to download
    SERVER  - You wont need to change this, unless you have your own data store.
    is_dir  - You wont need to change this, this is an internal param for downloaing a directory

    """

    print("MkNxGn CDN - GET: " + filedir)
    resp = requests.get(url=SERVER + "GET/" + filedir, stream=True)
    if resp.status_code == 200:
        if 'is_dir' in resp.headers:
            print("Downloading Directory:", filedir)
            files = resp.json()
            for file in files:
                path = os.path.split(file)[0]
                os.makedirs(path, exist_ok=True)
                CDN_Download(file, is_dir=True)
            print("DIR DOWNLOAD: OK")
        else:
            filesize = int(resp.headers['file_size'])
            if is_dir == False:
                filedir = os.path.split(filedir)[1]
            with open(filedir, "wb") as file:
                i = 0
                for chunk in resp.iter_content(chunk_size=500):
                    if chunk:
                        i += len(chunk)
                        file.write(chunk)
                        print(("Downloading: " + "█"*(int((i*40)/filesize))).ljust(54) + (str(round(i*0.000001, 3)).ljust(6, "0") + "/" + str(round(filesize*0.000001, 3)).ljust(6, "0") + " MB ") + "STATUS: DOWNLOADING", end="\r")
            print(("Downloading: " + "█"*(int((i*40)/filesize))).ljust(54) + (str(round(i*0.000001, 3)).ljust(6, "0") + "/" + str(round(filesize*0.000001, 3)).ljust(6, "0") + " MB ") + "STATUS: OK                     ")
    else:
        print("FAILED")


"""
The following is intended to record package loads.
Nothing about your person, location, or IP Address is recorded.

This task:
Runs in the background,
Keeps a maximum open time of 3 seconds,
Won't run if there is no internet.
Won't keep your program running if your program finishes before it does.
Boosts my moral to keep this package free and up to date.

This specific placement is to determine if anyone uses CDN

If you wish to not be apart of this program, please delete these next lines or change true to false.
"""

if True:
    try:
        import threading
        def bg():
            try:
                import requests
                response = requests.get("https://analyticscom.mknxgn.pro/rpg/mknxgn_essentials_CDN", timeout=3)
                # If you ever feel like deleting this, uncomment the line below...
                #print(response.text)
            except:
                pass
        threading.Thread(target=bg, daemon=True).start()
    except:
        pass