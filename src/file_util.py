import os

def mkdir(dir):
    os.makedirs(dir, exist_ok=True)

def read_binary(file):
    f=open(file, 'rb')
    data = f.read()
    f.close()
    return data

def write_binary(file, bin):
    f=open(file, "wb")
    f.write(bin)
    f.close

def write_txt(file, lines, insert_line_break=True, ignore_extention=False):
    if file[-4:]!=".txt" and not ignore_extention:
        raise ValueError("'file' should be a text file.")

    with open(file, "w", encoding='utf-8') as f:
        if insert_line_break:
            f.write("\n".join(lines)) 
        else:
            f.writelines(lines)
    #let lines=['a','b','c',...]
    #if insert_line_break:
    #   write 'a/n'+'b/n'+'c/n'+...
    #else:
    #   write 'abc...'

def get_filelist(dir, extention=None, root=""):
    l=[]
    for f in os.listdir(dir):
        file_path=os.path.join(dir,f)
        if os.path.isdir(file_path):
            l=l+get_filelist(file_path, extention=extention, root=os.path.join(root, f))
        else:
            if (extention is not None) and (f.split(".")[-1]!=extention):
                continue
            l.append(os.path.join(root,f))
    return sorted(l)

def write_filelist(dir, file_name, extention=None):
    l=get_filelist(dir,extention=extention)
    write_txt(file_name,l)

#sample
#print(get_filelist("./", extention="py"))
#write_filelist("./","test.txt",extention="py")