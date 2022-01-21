import os, copy
import file_util as util
import json

#---utils---

def get_file_size(f):
    pos=f.tell()
    f.seek(0, 2)
    size = f.tell()
    f.seek(pos)
    return size

def read_uint32(file):
    bin = file.read(4)
    return int.from_bytes(bin, 'little')

def read_int32(file):
    bin = file.read(4)
    return int.from_bytes(bin, 'little', signed=True)

def read_str(file):
    num = read_uint32(file)
    if num==0:
        return ""
    string = file.read(num-1).decode()
    file.seek(1,1)
    return string

def read_utf_str(file):
    num = read_int32(file)
    if num==0:
        return False, ""

    utf16 = num<0
    if utf16:
        num = -num

    string = file.read((num-1)*(utf16+1)).decode('utf-16-le'*utf16+'ascii'*(not utf16))
    if utf16:
        string=string.encode('utf-8').decode('utf-8')

    file.seek(utf16+1,1)
    return utf16, string

def write_uint32(file, n):
    bin = n.to_bytes(4, byteorder='little')
    file.write(bin)

def write_int32(file, n):
    bin = n.to_bytes(4, byteorder='little', signed=True)
    file.write(bin)

def write_str(file, s):
    if s=="":
        write_uint32(file, 0)
        return
    num = len(s)+1
    write_uint32(file, num)
    str_byte = s.encode()
    file.write(str_byte + b'\x00')

def write_utf_str(file, utf16, s):
    if s=="":
        write_uint32(file, 0)
        return
    num = len(s)+1
    if utf16:
        num = -num
    write_int32(file, num)
    str_byte = s.encode('utf-16-le'*utf16+'ascii'*(not utf16))
    file.write(str_byte + b'\x00'*(utf16+1))

#---objects---

class TextUexp:
    HEAD = b'\x00\x03'
    PAD = b'\x00\x00\x00\x00' #Null
    FOOT = b'\xC1\x83\x2A\x9E' #Unreal Header
    
    #I don't know how these integers works, but texts are separated by them 
    SEP  = [3, 4, 5, 12, 14]

    LANG_LIST = ['BR', 'CN', 'DE', 'ES', 'FR', 'IT', 'JP', 'KR', 'MX', 'TW', 'US']

    VERSION='1.4.2'

    def __init__(self, uexp_file_name=None, vorbose=False):
        self.vorbose=vorbose
        if uexp_file_name is not None:
            self.load(uexp_file_name)

    #load .uexp file and extract text data
    def load(self, uexp_file_name):
        if uexp_file_name[-5:]!='.uexp':
            raise RuntimeError('File extension error: Not .uexp')

        self.is_subtitle_file=os.path.basename(uexp_file_name)[:3].isdecimal()

        #load file
        self.file_name=uexp_file_name
        file = open(self.file_name, 'rb')
        self.header = file.read(2)
        self.lang = read_str(file) #US, JP, etc...
        zero = read_uint32(file)

        #check format
        if self.header != TextUexp.HEAD \
            or zero != 0 \
            or self.lang not in TextUexp.LANG_LIST:
            raise RuntimeError('Parse failed: Not text data')

        object_num = read_uint32(file)

        #extract text data
        self.text_object_list = []
        for i in range(object_num):
            #get id string
            id = read_str(file)
            if id[0]!='$':
                raise RuntimeError('Parse failed: ID not found')

            text_utf16, text = read_utf_str(file)

            text_num = read_uint32(file)

            sep_list=[]
            speaker_utf16_list=[]
            speaker_list=[]

            for j in range(text_num):
                sep=read_uint32(file)
                zero=read_uint32(file)
                if sep not in TextUexp.SEP or zero!=0:
                    raise RuntimeError('Parse failed: Unexpected separator found')
                sep_list.append(sep)

                speaker_utf16, speaker = read_utf_str(file)
                
                speaker_list.append(speaker)
                speaker_utf16_list.append(speaker_utf16)

            #add extracted data to the list
            text_object = {
                'id': id,
                'text':{'utf-16':text_utf16, 'str':text},
                'separator':sep_list,
                'speaker':{'utf-16':speaker_utf16_list, 'str':speaker_list}
                }
            self.text_object_list.append(text_object)

            #log
            if self.vorbose:
                print(id)
                print(text)
                print(speaker)

        foot = file.read(4)
        if foot!=TextUexp.FOOT: #Not found footer
            raise RuntimeError('Parse failed: Unreal signature not found')

        file.close()

    def list_simplify(list):
        if len(list)==1:
            list = list[0]
        elif len(list)==0:
            list = None
        return list

    def save_as_json(self, file):
        
        json_data = {}

        data = copy.deepcopy(self.text_object_list)
        for d in data:
            d['text']=d['text']['str']
            del d['separator']
            d['speaker']=TextUexp.list_simplify(d['speaker']['str'])
            if self.is_not_subtitle(d['id']):
                d['info']=d['speaker']
                del d['speaker']


        json_data['data']=data
        meta = {'tool':'FF7R text mod tools', 'version':TextUexp.VERSION, 'game':'FF7R'}
        json_data['meta']=meta
        with open(file , 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

    #Whether 2 strings are the same or not.
    #it consider letter case and some conjugations of verbs.
    def is_same_word(s1,s2):
        m = min(len(s1), len(s2))
        if m==1:
            return s1.lower()==s2.lower()
        return s1[:m-1].lower()==s2[:m-1].lower()

    #merge single text.
    def merge_string(self, s1, utf16_1, s2, utf16_2, not_subtitle, just_swap, reject_similar_word=False):

        if s1=="" or just_swap:
            return s2, utf16_2
        if s2=="":
            return s1, utf16_1

        if (not self.is_subtitle_file) and reject_similar_word and TextUexp.is_same_word(s1, s2):
            return s1, utf16_1

        #insert line feed
        lf = '\r\n'
        if not_subtitle and not (lf in s1 or lf in s2):#for non subtitle data
                lf = ' / '

        #merge (or swap) text
        new_s = s1+lf+s2
        new_utf16=utf16_1 or utf16_2

        return new_s, new_utf16


    def is_not_subtitle(self, id):
        if self.is_subtitle_file:
            return id[0:6]=='$level' or (id[-3]!='0' and id[-12:-8]=='_900' and id[-7:-3]=='_cut' )
        else:
            id_=id[-5:]
            return not (id_=="chd_0" or id_=="art_0" or id_=="cld_0")


    def merge_text(self, text_object_list, just_swap=False, mod_all=False, reject_similar_word=False):
        err_msg='Merge'*(not just_swap)+'Replacement'*just_swap+' failed: '
        if len(self.text_object_list)!=len(text_object_list):
            raise RuntimeError(err_msg+'Number of objects does not match')
        
        i=0
        for t, t2 in zip(self.text_object_list, text_object_list):
            #check format
            id, id2 = t['id'], t2['id']
            if id!=id2:
                raise RuntimeError(err_msg+'IDs are not the same. ({} and {})'.format(id, id2))            
            
            not_subtitle = self.is_not_subtitle(id)

            if not_subtitle and not mod_all:
                continue
            
            #merge text
            utf16 = t['text']['utf-16']
            text = t['text']['str']            
            utf16_2 = t2['text']['utf-16']
            text_2 = t2['text']['str']
            new_text, new_utf16 = self.merge_string(text, utf16, text_2, utf16_2, not_subtitle, just_swap, reject_similar_word=reject_similar_word)
            t['text']={'utf-16':new_utf16, 'str':new_text}

            if not mod_all:
                continue

            speaker1 = t['speaker']['str']
            speaker2 = t2['speaker']['str']
            speaker1_utf = t['speaker']['utf-16']
            speaker2_utf = t2['speaker']['utf-16']
            new_speaker=[]
            new_speaker_utf=[]
            l1=len(speaker1)
            l2=len(speaker2)
            if l1>l2:
                speaker2_utf=[False]*(l1-l2)+speaker2_utf
                speaker2=['']*(l1-l2)+speaker2
            for s1_utf, s1, s2_utf, s2 in \
                zip(speaker1_utf, speaker1, speaker2_utf, speaker2):
                new_s, new_s_utf = self.merge_string(s1, s1_utf, s2, s2_utf, True, just_swap, reject_similar_word=reject_similar_word)
                new_speaker.append(new_s)
                new_speaker_utf.append(new_s_utf)
            
            t['speaker']={'utf-16':new_speaker_utf, 'str':new_speaker}

    def save_as_uexp(self, file_name, reject_empty_data=False):
        #check uasset exist
        if not os.path.isfile(self.file_name[:-4]+'uasset'):
            raise RuntimeError('File not found: '+self.file_name[:-4]+'uasset')

        if reject_empty_data and len(self.text_object_list)==0:
            return False

        file = open(file_name, 'wb')

        file.write(self.header)
        write_str(file, self.lang)
        write_uint32(file, 0)
        write_uint32(file, len(self.text_object_list))
        for t in self.text_object_list:
            #write id
            id = t['id']
            write_str(file, id)

            #write main text (subtitle text)
            write_utf_str(file, t['text']['utf-16'], t['text']['str'])

            #write other texts
            write_uint32(file, len(t['separator']))
            for sep, speaker_utf16, speaker in zip(t['separator'], t['speaker']['utf-16'], t['speaker']['str']):
                write_uint32(file, sep)
                write_uint32(file, 0)
                write_utf_str(file, speaker_utf16, speaker)

        new_uexp_size=file.tell()
        file.write(TextUexp.FOOT)

        #write a new .uexp file
        file.close()

        #write a new .uasset file
        new_uexp_size_bin=new_uexp_size.to_bytes(4, 'little')

        uasset_bin = util.read_binary(self.file_name[:-4]+'uasset')
        util.write_binary(file_name[:-4]+'uasset', uasset_bin[:-92]+new_uexp_size_bin+uasset_bin[-88:])
        return True


    def comp_ver(v1,v2):#v1>v2
        def v_to_int(v):
            v = v.split('.')
            v = int(v[0])*10000+int(v[1])*100+int(v[2])
            return v
        v1 = v_to_int(v1)
        v2 = v_to_int(v2)
        return v1>v2

    def swap_with_json(self, json_file):

        with open(json_file, 'r', encoding='utf-8') as f:
            uexp_as_json = json.load(f)
        
        if 'meta' in uexp_as_json:#version >= 1.3.1
            meta = uexp_as_json['meta']
            ver = meta['version']
            text_object_list2=uexp_as_json['data']

        else:#version <= 1.3.0
            ver = '1.3.0'

        def to_list(var):
            if var is None:
                var = []
            if type(var)!=type([]):
                var = [var]
            return var

        def is_list(l):
            return type(l)==type([])

        def is_not_ascii(s):
            if s is None:
                return None
            return len(s) != len(s.encode())

        def get_utf16_list(text_list):
            utf16_list=[]
            for text in text_list:
                utf16_list.append(is_not_ascii(text))
            return utf16_list

        def fix_label(text_object_list):
            for t in text_object_list:
                t['speaker']=t['talker']
                del t['talker']

        if TextUexp.comp_ver('1.4.0', ver):#version<1.4.0
            print('Warning: This json file was exported by an old version.\r\n'+ \
                  '         It will be uncompatible in the future')

        if ver=='1.3.0':
            text_object_list2=[]
            for i in range(len(self.text_object_list)):
                t = uexp_as_json[str(i)]
                t['id']=t['id']['str']
                text_object_list2.append(t)
                fix_label(text_object_list2)

        elif TextUexp.comp_ver('1.3.3', ver):
            #if 1.3.0 < version < 1.3.3
            with open(json_file, 'r') as f:
                uexp_as_json = json.load(f)
            text_object_list2=uexp_as_json['data']
            fix_label(text_object_list2)

        elif ver=='1.3.3':
            fix_label(text_object_list2)
        
        elif TextUexp.comp_ver('1.4.0', ver):
            #if 1.3.3 < version < 1.4.0
            for t in text_object_list2:
                text_str = to_list(t['text'])
                text_utf16 = get_utf16_list(text_str)
                t['text']={'utf-16':text_utf16, 'str':text_str}
                talker=t['talker']
                t['talker']={'utf-16':is_not_ascii(talker), 'str':talker}
            fix_label(text_object_list2)
        
        elif TextUexp.comp_ver('1.4.2', ver):
            #if 1.4.0 <= version < 1.4.2
            for t in text_object_list2:
                text_str = to_list(t['text'])
                text_utf16 = get_utf16_list(text_str)
                t['text']={'utf-16':text_utf16, 'str':text_str}
                speaker=t['speaker']
                t['speaker']={'utf-16':is_not_ascii(speaker), 'str':speaker}
        
        else: #if version >= 1.4.2
            for t in text_object_list2:
                text = t['text']
                t['text']={'utf-16':is_not_ascii(text), 'str':text}
                if 'speaker' not in t:
                    key='info'
                else:
                    key='speaker'
                speaker_str = to_list(t[key])
                speaker_utf16 = get_utf16_list(speaker_str)
                t['speaker']={'utf-16':speaker_utf16, 'str':speaker_str}

        if TextUexp.comp_ver('1.4.2', ver):
            # if version < 1.4.2
            for t in text_object_list2:
                text = t['text']['str']
                utf=t['text']['utf-16']
                if text is None:
                    text=''
                    utf=False
                text_utf = TextUexp.list_simplify(utf)
                text_str = TextUexp.list_simplify(text)
                if text_str is None:
                    text_str=''
                    text_utf=False
                speaker_utf = to_list(t['speaker']['utf-16'])
                speaker_str = to_list(t['speaker']['str'])
                if is_list(text_str):
                    speaker_utf=text_utf[1:]+speaker_utf
                    speaker_str=text_str[1:]+speaker_str
                    text_utf = text_utf[0]
                    text_str = text_str[0]
                t['text']={'utf-16':text_utf, 'str':text_str}
                t['speaker']={'utf-16':speaker_utf, 'str':speaker_str}
                
        self.merge_text(text_object_list2, just_swap=True, mod_all=all)

    def save_as_txt(self, txt_file):
        f=open(txt_file, 'w', encoding='utf-8')
        
        for t in self.text_object_list:
            text = t['text']['str']
            speaker_list = t['speaker']['str']

            if speaker_list==[]:
                speaker='***'
                f.write(speaker+'\n')

            for speaker in speaker_list:
                if speaker=='':
                    speaker='***'
                f.write(speaker+'\n')

            if text!='':
                text = text.split('\r\n')
                
                for l in text:
                    if l=='':
                        continue
                    f.write('   '+l+'\n')

            f.write('\n')

        if len(self.text_object_list)==0:
            f.write('Empty file')

        f.close()




