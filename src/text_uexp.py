import os, copy
import file_util as util
import json

class TextUexp:
    HEAD = b"\x00\x03\x03\x00"
    PAD = b"\x00\x00\x00\x00" #Null
    FOOT = b"\xC1\x83\x2A\x9E" #Unreal Header
    
    #I don't know how these byte data works, but texts are separated by them 
    SEP  = [b"\x04\x00\x00\x00\x00\x00\x00\x00", \
            b"\x03\x00\x00\x00\x00\x00\x00\x00", \
            b"\x05\x00\x00\x00\x00\x00\x00\x00", \
            b"\x0C\x00\x00\x00\x00\x00\x00\x00", \
            b"\x0E\x00\x00\x00\x00\x00\x00\x00"]

    LANG_LIST = ["BR", "CN", "DE", "ES", "FR", "IT", "JP", "KR", "MX", "TW", "US"]

    VERSION="1.3.5"

    #read string data
    def read_str(file):
        num_byte = file.read(4)
        num = int.from_bytes(num_byte, "little", signed=True)

        if num==0:
            return None, None

        utf16 = num<0
        if utf16:
            num = -num

        sep_id = num*(utf16+1)

        string = file.read(sep_id-(utf16+1)).decode("utf-16-le"*utf16+"ascii"*(not utf16))
        if utf16:
            string=string.encode('utf-8').decode('utf-8')

        file.read(utf16+1)
        return utf16, string

    #load .uexp file and extract text data
    def __init__(self, uexp_file_name, vorbose=False):
        if uexp_file_name[-5:]!=".uexp":
            raise RuntimeError("file extension error (not .uexp)")

        self.is_subtitle_file=os.path.basename(uexp_file_name)[:3].isdecimal()

        #load file
        self.file_name=uexp_file_name
        file = open(self.file_name, 'rb')
        self.header = file.read(17)
        self.lang = self.header[6:8].decode("ascii") #e.g. 55 53 (US)

        #check format
        if self.header[0:4] != TextUexp.HEAD \
            or self.header[8:13] != TextUexp.PAD+b"\x00" \
            or self.lang not in TextUexp.LANG_LIST:
            raise RuntimeError("format error 1: Not subtitle uexp")

        object_num = int.from_bytes(self.header[13:17], "little", signed=True)

        #extract text data
        file_size = os.path.getsize(self.file_name)-4
        self.text_object_list = []
        while (file.tell()<file_size):
            #get id string
            _, id = TextUexp.read_str(file)
            if id[0]!="$":
                raise RuntimeError("format error 3: Failed to parse")

            text_utf16, text = TextUexp.read_str(file)
            if text is None:
                text_list=[]
                text_utf16_list=[]
            else:
                text_list=[text]
                text_utf16_list=[text_utf16]
            

            text_num = int.from_bytes(file.read(4), 'little')
            
            sep=file.read(8)
            if sep in TextUexp.SEP:
                sep_type = TextUexp.SEP.index(sep)
                sep_type_list=[sep_type]
            else:
                if text_num!=0:
                    print(text)
                    raise RuntimeError("format error 4: Failed to parse")
                file.seek(file.tell()-12)
                sep_type_list=[]
                text_num=1

            #get other texts (sometimes, non subtitle data has more texts.)            
            if text_num>=2:
                for i in range(text_num-1):
                    text_utf16, text = TextUexp.read_str(file)
                    sep = file.read(8)
                    if sep in TextUexp.SEP:
                        sep_type = TextUexp.SEP.index(sep)
                    else:
                        raise RuntimeError("format error 5: Failed to parse")
                    
                    text_list.append(text)
                    text_utf16_list.append(text_utf16)
                    sep_type_list.append(sep_type)

                if sep_type!=4:
                    raise RuntimeError("format error 6: Failed to parse")

            #get talker's name
            talker_utf16, talker = TextUexp.read_str(file)

            if talker is None:
                talker_utf16=False
                talker=""

            #add extracted data to the list
            text_object = {
                "id": id,
                "text":{"utf-16":text_utf16_list, "str":text_list},
                "sep_type":sep_type_list,
                "talker":{"utf-16":talker_utf16, "str":talker}
                }
            self.text_object_list.append(text_object)

            #log
            if vorbose:
                print(id)
                print(text)
                print(talker)

        foot = file.read(4)
        if foot!=TextUexp.FOOT: #Not found footer
            raise RuntimeError("format error 2: Not uexp")
        
        #check the format
        if len(self.text_object_list)!=object_num:
            raise RuntimeError("Parse failed. Number of objects does not match.")

        file.close()

    TYPE_LIST=type([])

    def save_as_json(self, file):
        
        json_data = {}

        def list_simplify(list):
            if len(list)==1:
                list = list[0]
            elif len(list)==0:
                list = None
            return list

        data = copy.deepcopy(self.text_object_list)
        for d in data:
            text = d["text"]["str"]
            text = list_simplify(text)
            d["text"]=text
            del d["sep_type"]
            d["talker"]=d["talker"]["str"]

        json_data["data"]=data
        meta = {"tool":"FF7R text mod tools", "version":TextUexp.VERSION}
        json_data["meta"]=meta
        with open(file , 'w', encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

    #Whether 2 strings are the same or not.
    #it consider letter case and some conjugations of verbs.
    def is_same_word(s1,s2):
        m = min(len(s1), len(s2))
        if m==1:
            return s1.lower()==s2.lower()
        return s1[:m-1].lower()==s2[:m-1].lower()

    #merge single text.
    def merge_string(self, s1, utf16_1, s2, utf16_2, not_subtitle, just_swap):
        new_utf16=utf16_1 or utf16_2

        #insert line feed
        lf = "\r\n"
        if not_subtitle and not (lf in s1 or lf in s2):#for non subtitle data
                lf = " / "

        #merge (or swap) text
        if just_swap:
            new_s = s2
        else:
            new_s = s1+lf+s2
        
        if (not self.is_subtitle_file) and TextUexp.is_same_word(s1, s2):
            new_s=s1
            new_utf16=utf16_1

        return new_s, new_utf16


    def merge_text(self, text_object_list, just_swap=False, mod_all=False):
        if len(self.text_object_list)!=len(text_object_list):
            raise RuntimeError("Merge failed. Number of objects does not match.")
        
        i=0
        for t, t2 in zip(self.text_object_list, text_object_list):

            utf16_list = t["text"]["utf-16"]
            text_list = t["text"]["str"]
            
            utf16_list_2 = t2["text"]["utf-16"]
            text_list_2 = t2["text"]["str"]

            if len(text_list)==0 or len(text_list_2)==0:
                continue

            #check format
            id = t["id"]
            if t["id"]!=t2["id"]:
                raise RuntimeError("Merge failed. The structure is not the same.")
            
            talker1 = t["talker"]["str"]
            talker2 = t2["talker"]["str"]
            if self.is_subtitle_file:
                not_subtitle = id[0:6]=="$level" or (id[-3]!="0" and id[-12:-8]=="_900" and id[-7:-3]=="_cut" )
            else:
                not_subtitle = not (t["sep_type"]==[1] and talker1!="")

            if not_subtitle and not mod_all:
                continue

            i=0
            for text, utf16 in zip(text_list, utf16_list):
                if i>=len(text_list_2):
                    i+=1
                    break
                
                text_2=text_list_2[i]
                utf16_2=utf16_list_2[i]
                new_text, new_utf16 = self.merge_string(text, utf16, text_2, utf16_2, not_subtitle, just_swap)
                
                text_list[i]=new_text
                utf16_list[i]=new_utf16
                i+=1

            #merge talker's name
            if mod_all and talker1!="" and talker2!="":
                new_talker, new_utf16 = self.merge_string(talker1, t["talker"]["utf-16"], talker2, t2["talker"]["utf-16"], True, just_swap)
                t["talker"]={"utf-16":new_utf16, "str":new_talker}

    def str_to_bin(utf16, s):
        num = len(s)+1
        if utf16:
            num = -num
        num_byte = num.to_bytes(4, 'little', signed=True)
        str_byte = s.encode("utf-16-le"*utf16+"ascii"*(not utf16))
        return num_byte + str_byte + b"\x00"*(utf16+1)

    def save_as_uexp(self, file_name):
        #check uasset exist
        if not os.path.isfile(self.file_name[:-4]+"uasset"):
            raise RuntimeError("Not found "+self.file_name[:-4]+"uasset")

        file = open(file_name, "wb")

        file.write(self.header)
        for t in self.text_object_list:
            #add id data
            id = t["id"]
            file.write(TextUexp.str_to_bin(False, id))

            #add text 1 data (may be subtitle text)
            text_list = t["text"]["str"]
            text_utf16_list = t["text"]["utf-16"]
            sep_type_list = t["sep_type"]
            if len(text_list)==0:
                file.write(TextUexp.PAD)
                if len(sep_type_list)>0:
                    file.write(b"\x01\x00\x00\x00")
                    file.write(TextUexp.SEP[sep_type_list[0]])
            else:
                file.write(TextUexp.str_to_bin(text_utf16_list[0], text_list[0]))
                if len(sep_type_list)>0:
                    file.write(len(text_list).to_bytes(4, byteorder="little"))
                    file.write(TextUexp.SEP[sep_type_list[0]])
                
                #add other text data
                for i in range(len(text_list)-1):
                    file.write(TextUexp.str_to_bin(text_utf16_list[i+1], text_list[i+1]))
                    file.write(TextUexp.SEP[sep_type_list[i+1]])

            #add talker's name
            talker = t["talker"]
            if talker["str"]=="":
                file.write(TextUexp.PAD)
            else:
                file.write(TextUexp.str_to_bin(talker["utf-16"], talker["str"]))
        file.write(TextUexp.FOOT)

        #write a new .uexp file
        file.close()

        #write a new .uasset file
        new_uexp_size = os.path.getsize(file_name)-4
        new_uexp_size_bin=new_uexp_size.to_bytes(4, 'little', signed=True)

        uasset_bin = util.read_binary(self.file_name[:-4]+"uasset")
        util.write_binary(file_name[:-4]+"uasset", uasset_bin[:-92]+new_uexp_size_bin+uasset_bin[-88:])


    def comp_ver(v1,v2):#v1>v2
        def v_to_int(v):
            v = v.split(".")
            v = int(v[0])*10000+int(v[1])*100+int(v[2])
            return v
        v1 = v_to_int(v1)
        v2 = v_to_int(v2)
        return v1>v2

    def swap_with_json(self, json_file):

        with open(json_file, 'r', encoding="utf-8") as f:
            uexp_as_json = json.load(f)
        
        if "meta" in uexp_as_json:#version >= 1.3.1
            meta = uexp_as_json["meta"]
            ver = meta["version"]
            text_object_list2=uexp_as_json["data"]

        else:#version <= 1.3.0
            ver = "1.3.0"

        def to_list(var):
            if var is None:
                var = []
            if type(var)!=TextUexp.TYPE_LIST:
                var = [var]
            return var

        def is_not_ascii(s):
            """Check if the characters in string s are in ASCII, U+0-U+7F."""
            return len(s) != len(s.encode())

        def get_utf16_list(text_list):
            utf16_list=[]
            for text in text_list:
                utf16_list.append(is_not_ascii(text))
            return utf16_list


        if TextUexp.comp_ver(ver, "1.3.3"):#if version > 1.3.3
            for t in text_object_list2:
                text_str = to_list(t["text"])
                text_utf16 = get_utf16_list(text_str)
                t["text"]={"utf-16":text_utf16, "str":text_str}
                talker=t["talker"]
                t["talker"]={"utf-16":is_not_ascii(talker), "str":talker}
        
        elif ver=="1.3.0":
            text_object_list2=[]
            for i in range(len(self.text_object_list)):
                t = uexp_as_json[str(i)]
                t["id"]=t["id"]["str"]
                text_object_list2.append(t)

        elif TextUexp.comp_ver("1.3.3", ver):#if version < 1.3.3
            with open(json_file, 'r') as f:
                uexp_as_json = json.load(f)
            text_object_list2=uexp_as_json["data"]

        
        
        self.merge_text(text_object_list2, just_swap=True, mod_all=all)

    def save_as_txt(self, txt_file):
        txt_data = []
        for t in self.text_object_list:
            text_list = t["text"]["str"]
            talker = t["talker"]["str"]

            if len(text_list)==0:
                continue

            if talker=="":
                talker="***"

            txt_data.append(talker)


            for text in text_list:
                text = text.split("\r\n")
                
                for l in text:
                    if l=="":
                        continue
                    txt_data.append("   "+l)

            txt_data.append("")

        if len(txt_data)==0:
            txt_data.append("Empty file")

        util.write_txt(txt_file, txt_data)




