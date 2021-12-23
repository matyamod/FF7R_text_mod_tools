import os
import file_util as util
import json
import warnings

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

    #pop string data
    def pop_str(bin):
        num = int.from_bytes(bin[0:4], "little", signed=True)
        if num<0:
            num = -num
            utf16 = True
        else:
            utf16 = False
        sep_id = 4+num*(utf16+1)
        str = bin[4:sep_id-(utf16+1)].decode("utf-16-le"*utf16+"ascii"*(not utf16))
        return utf16, str, bin[sep_id:]

    #load .uexp file and extract text data
    def __init__(self, uexp_file, vorbose=False):
        if uexp_file[-5:]!=".uexp":
            raise RuntimeError("file extension error (not .uexp)")

        self.is_subtitle=os.path.basename(uexp_file)[:3].isdecimal()

        #load file
        self.file=uexp_file
        bin = util.read_binary(self.file)
        self.header = bin[0:17]
        self.lang = self.header[6:8].decode("ascii") #00 00 55 53 (US)

        #check format
        if self.header[0:4] != TextUexp.HEAD \
            or self.header[8:13] != TextUexp.PAD+b"\x00" \
            or self.lang not in TextUexp.LANG_LIST:
            raise RuntimeError("format error 1: Not subtitle uexp")

        object_num = int.from_bytes(self.header[13:17], "little", signed=True)

        #extract text data
        data = bin[17:]
        self.text_object_list = []
        while (data != TextUexp.FOOT):
            if len(data)<4: #Not found footer
                raise RuntimeError("format error 2: Not uexp")

            #get id string
            id_utf16, id, data = TextUexp.pop_str(data)
            if id[0]!="$":
                raise RuntimeError("format error 3: Failed to parse")

            #get text 1 (may be subtitle text)
            if data[0:4]==TextUexp.PAD:
                text_list=[]
                text_utf16_list=[]
                data = data[4:]
            else:
                text_utf16, text, data = TextUexp.pop_str(data)
                text_list=[text]
                text_utf16_list=[text_utf16]
            

            text_num = int.from_bytes(data[0:4], 'little')
            
            sep=data[4:12]
            if sep in TextUexp.SEP:
                sep_type = TextUexp.SEP.index(sep)
                sep_type_list=[sep_type]
                data = data[12:]
            else:
                if text_num!=0:
                    print(text)
                    raise RuntimeError("format error 4: Failed to parse")
                sep_type_list=[]
                text_num=1

            #get other texts (sometimes, non subtitle data has more texts.)            
            if text_num>=2:
                for i in range(text_num-1):
                    text_utf16, text, data = TextUexp.pop_str(data)
                    if data[0:8] in TextUexp.SEP:
                        sep_type = TextUexp.SEP.index(data[0:8])
                        data=data[8:]
                    else:
                        raise RuntimeError("format error 5: Failed to parse")
                    
                    text_list.append(text)
                    text_utf16_list.append(text_utf16)
                    sep_type_list.append(sep_type)

                if sep_type!=4:
                    raise RuntimeError("format error 6: Failed to parse")

            #get talker's name
            if data[0:4]==TextUexp.PAD:
                talker_utf16=False
                talker=""
                data = data[4:]
            else:
                talker_utf16, talker, data = TextUexp.pop_str(data)
            
            #add extracted data to the list
            text_object = {
                "id": {"utf-16": id_utf16, "str":id },
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
        
        #check the format
        if len(self.text_object_list)!=object_num:
            raise RuntimeError("Parse failed. Number of objects does not match.")

    def save_as_json(self, file):
        json_data = {}
        i=0
        for t in self.text_object_list:
            json_data[i]=t
            i+=1

        with open(file, 'w') as f:
            json.dump(json_data, f, indent=4)

    #Whether 2 strings are the same or not.
    #it consider letter case and some conjugations of verbs.
    def is_same_word(s1,s2):
        m = min(len(s1), len(s2))
        if m==1:
            return s1.lower()==s2.lower()
        return s1[:m-1].lower()==s2[:m-1].lower()

    #merge single text.
    def merge_string(self, s1, utf16_1, s2, utf16_2, no_lf, just_swap):
        new_utf16=utf16_1 or utf16_2

        #encoding
        if utf16_1 and (not utf16_2):
            s2=s2.encode("utf-16-le").decode("utf-16-le")
        if (not utf16_1) and utf16_2:
            s1=s1.encode("utf-16-le").decode("utf-16-le")

        #insert line feed
        lf = "\r\n"
        if no_lf and (not lf in s1) and (not lf in s2):#for non subtitle data
                lf = " / "

        if new_utf16:
            lf=lf.encode("utf-16-le").decode("utf-16-le")

        #merge (or swap) text
        if just_swap:
            new_s = s2
        else:
            new_s = s1+lf+s2
        
        if (not self.is_subtitle) and TextUexp.is_same_word(s1, s2):
            new_s=s1

        return new_s, new_utf16


    def merge_text(self, text_object_list, just_swap=False):
        if len(self.text_object_list)!=len(text_object_list):
            raise RuntimeError("Merge failed. Number of objects does not match.")
        
        i=0
        for t2 in text_object_list:

            utf16_list_2 = t2["text"]["utf-16"]
            text_list_2 = t2["text"]["str"]

            t = self.text_object_list[i]
            utf16_list = t["text"]["utf-16"]
            text_list = t["text"]["str"]

            if len(text_list)==0 or len(text_list_2)==0:
                i+=1
                continue

            #check format
            if t["id"]["str"]!=t2["id"]["str"]:
                raise RuntimeError("Merge failed. The structure is not the same.")
            
            new_utf16_list=[]
            new_text_list=[]
            for j in range(len(text_list)):
                if j>=len(text_list_2):
                    break
                
                text=text_list[j]
                utf16=utf16_list[j]
                text_2=text_list_2[j]
                utf16_2=utf16_list_2[j]
                new_text, new_utf16 = self.merge_string(text, utf16, text_2, utf16_2, (not self.is_subtitle), just_swap)
                
                new_text_list.append(new_text)
                new_utf16_list.append(new_utf16)

            self.text_object_list[i]["text"]={"utf-16":new_utf16_list, "str":new_text_list}
            
            #merge talker's name
            talker1 = t["talker"]["str"]
            talker2 = t2["talker"]["str"]
            if talker1!="" and talker2!="":
                new_talker, new_utf16 = self.merge_string(talker1, t["talker"]["utf-16"], talker2, t2["talker"]["utf-16"], True, just_swap)
                self.text_object_list[i]["talker"]={"utf-16":new_utf16, "str":new_talker}
            i+=1

    def str_to_bin(utf16, str):
        num = len(str)+1
        if utf16:
            num = -num
        num_byte = num.to_bytes(4, 'little', signed=True)
        str_byte = str.encode("utf-16-le"*utf16+"ascii"*(not utf16))
        return num_byte + str_byte + b"\x00"*(utf16+1)

    def save_as_uexp(self, file):
        #check uasset exist
        if not os.path.isfile(self.file[:-4]+"uasset"):
            raise RuntimeError("Not found "+self.file[:-4]+"uasset")

        data = self.header
        for t in self.text_object_list:
            #add id data
            id = t["id"]
            data += TextUexp.str_to_bin(id["utf-16"], id["str"])

            #add text 1 data (may be subtitle text)
            text_list = t["text"]["str"]
            text_utf16_list = t["text"]["utf-16"]
            sep_type_list = t["sep_type"]
            if len(text_list)==0:
                data += TextUexp.PAD
                if len(sep_type_list)>0:
                    data +=b"\x01\x00\x00\x00"
                    data += TextUexp.SEP[sep_type_list[0]]
            else:
                
                data += TextUexp.str_to_bin(text_utf16_list[0], text_list[0])
                if len(sep_type_list)>0:
                    data += len(text_list).to_bytes(4, byteorder="little")
                    data += TextUexp.SEP[sep_type_list[0]]
                
                #add other text data
                for i in range(len(text_list)-1):
                    data += TextUexp.str_to_bin(text_utf16_list[i+1], text_list[i+1])
                    data += TextUexp.SEP[sep_type_list[i+1]]

            #add talker's name
            talker = t["talker"]
            if talker["str"]=="":
                data += TextUexp.PAD
            else:
                data += TextUexp.str_to_bin(talker["utf-16"], talker["str"])
        data += TextUexp.FOOT

        #write a new .uexp file
        util.write_binary(file, data)

        #write a new .uasset file
        new_uexp_size = os.path.getsize(file)-4
        new_uexp_size_bin=new_uexp_size.to_bytes(4, 'little', signed=True)

        uasset_bin = util.read_binary(self.file[:-4]+"uasset")
        util.write_binary(file[:-4]+"uasset", uasset_bin[:-92]+new_uexp_size_bin+uasset_bin[-88:])

    def swap_with_json(self, json_file):
        with open(json_file) as f:
            uexp_as_json = json.load(f)
        
        text_object_list2=[]
        for i in range(len(self.text_object_list)):
            text_object_list2.append(uexp_as_json[str(i)])
        
        self.merge_text(text_object_list2, just_swap=True)

    def save_as_txt(self, txt_file):
        txt_data = []
        for t in self.text_object_list:
            text_list = t["text"]["str"]
            text_utf16_list = t["text"]["utf-16"]
            talker = t["talker"]["str"]

            if len(text_list)==0:
                continue

            if talker=="":
                talker="***"

            if t["talker"]["utf-16"]:
                talker = talker.encode("utf-8").decode("utf-8")
                
            txt_data.append(talker)


            for i in range(len(text_list)):
                text = text_list[i]
                if text_utf16_list[i]:
                    text = text.encode("utf-8").decode("utf-8")
                text = text.split("\r\n")
                
                for l in text:
                    if l=="":
                        continue
                    txt_data.append("   "+l)

            txt_data.append("")

        if len(txt_data)==0:
            txt_data.append("Empty file")

        util.write_txt(txt_file, txt_data)




