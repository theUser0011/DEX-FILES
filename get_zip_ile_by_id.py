import gdown


def download_zip(file_id,num1,num2):
        
    lst = [0, 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000, 72000, 80000, 88000, 96000, 104000, 112000, 120000, 128000, 136000, 144000, 152000, 160000, 168000, 176000, 184000, 192000, 200000, 208000, 216000, 224000, 232000, 240000, 248000, 256000, 264000, 272000, 280000, 288000, 296000]

    start = lst[num1]
    end = lst[num2]


    # Output file name
    output = "downloaded_file.zip"

    # Download the file
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)

    return [start,end]