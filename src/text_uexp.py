import os
import file_util as util
import json
import warnings

class TextUexp:
    HEAD = b"\x00\x03\x03\x00"
    PAD = b"\x00\x00\x00\x00"
    TAIL = b"\xC1\x83\x2A\x9E"
    
    SEP  = [b"\x01\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00", b"\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00", b"\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00"]
    ESEP = b"\x0E\x00\x00\x00\x00\x00\x00\x00"

    LANG_LIST = ["BR", "CN", "DE", "ES", "FR", "IT", "JP", "KR", "MX", "TW", "US"]

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

    def __init__(self, uexp_file, vorbose=False):
        if uexp_file[-5:]!=".uexp":
            raise("file extension error (not .uexp)")

        if not os.path.basename(uexp_file)[:3].isdecimal():
            warnings.warn("This file might be unexpected one. ("+uexp_file+")")


        self.file=uexp_file
        bin = util.read_binary(self.file)
        self.header = bin[0:17]
        self.lang = self.header[6:8].decode("ascii") #00 00 55 53 (US)

        #checks format
        if self.header[0:4] != TextUexp.HEAD \
            or self.header[8:12] != TextUexp.PAD \
            or self.lang not in TextUexp.LANG_LIST:
            raise("format error 1: Not subtitle uexp")
        
        data = bin[17:]
        
        self.text_object_list = []

        while (data != TextUexp.TAIL):
            if len(data)<4:
                raise("format error 2: Not uexp")
            id_utf16, id_file, data = TextUexp.pop_str(data)
            if id_file[0]!="$":
                raise("format error 3: Failed to parse")

            if data[0:4]==TextUexp.PAD:
                text_utf16=False
                text=""
                data = data[4:]    
            else:
                text_utf16, text, data = TextUexp.pop_str(data)
            
            sep=data[0:12]
            if sep in TextUexp.SEP:
                sep_type = TextUexp.SEP.index(sep)
                data = data[12:]
            else:
                sep_type=len(TextUexp.SEP)

            if sep_type==2:
                text2_utf16, text2, data = TextUexp.pop_str(data)
                if data[0:8]==TextUexp.ESEP:
                    esep=True
                    data=data[8:]
                else:
                    esep=False
            else:
                text2_utf16=False
                text2=""

            if data[0:4]==TextUexp.PAD:
                talker_utf16=False
                talker=""
                data = data[4:]
            else:
                talker_utf16, talker, data = TextUexp.pop_str(data)
            
            text_object = {
                "id": {"utf-16": id_utf16, "str":id_file },
                "text":{"utf-16":text_utf16, "str":text},
                "sep_type":sep_type,
                "talker":{"utf-16":talker_utf16, "str":talker}
                }
            if sep_type==2:
                text_object["text2"]={"utf-16":text2_utf16, "str":text2}
                text_object["esep"]=esep

            if vorbose:
                print(id_file)
                print(text)
                print(talker)
            
            self.text_object_list.append(text_object)

    def save_as_json(self, file):
        json_data = {}
        i=0
        for t in self.text_object_list:
            json_data[i]=t
            i+=1

        with open(file, 'w') as f:
            json.dump(json_data, f, indent=4)

    def merge_text(self, text_object_list, just_swap=False):
        i=0
        for t2 in text_object_list:
            
            utf16_2 = t2["text"]["utf-16"]
            text_2 = t2["text"]["str"]
            if text_2=="" or t2["sep_type"]==2:
                i+=1
                continue

            t = self.text_object_list[i]
            utf16 = t["text"]["utf-16"]
            text = t["text"]["str"]
            if text=="" or t["sep_type"]==2:
                i+=1
                continue

            #check id
            if t["id"]["str"]!=t2["id"]["str"]:
                raise("Failed to merge. Structure is not the same.")
                
            #encoding
            new_utf16=utf16 or utf16_2
            if utf16 and (not utf16_2):
                text_2=text_2.encode("utf-16-le").decode("utf-16-le")
            if (not utf16) and utf16_2:
                text=text.encode("utf-16-le").decode("utf-16-le")
            lf = "\r\n"
            if new_utf16:
                lf=lf.encode("utf-16-le").decode("utf-16-le")

            #merge (or swap) text
            if just_swap:
                new_text = text_2
            else:
                new_text = text+lf+text_2

            self.text_object_list[i]["text"]={"utf-16":new_utf16, "str":new_text}
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
            raise("Not found "+self.file[:-4]+"uasset")

        data = self.header
        for t in self.text_object_list:
            id = t["id"]
            data += TextUexp.str_to_bin(id["utf-16"], id["str"])
            text = t["text"]
            if text["str"]=="":
                data += TextUexp.PAD
            else:
                data += TextUexp.str_to_bin(text["utf-16"], text["str"])
            if t["sep_type"]<len(TextUexp.SEP):
                data += TextUexp.SEP[t["sep_type"]]
            if t["sep_type"]==2:
                text2 = t["text2"]
                data += TextUexp.str_to_bin(text2["utf-16"], text2["str"])
                if t["esep"]:
                    data += TextUexp.ESEP

            talker = t["talker"]
            if talker["str"]=="":
                data += TextUexp.PAD
            else:
                data += TextUexp.str_to_bin(talker["utf-16"], talker["str"])
        data += TextUexp.TAIL
        util.write_binary(file, data)

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




