#standard
import os, webbrowser, json, argparse

#tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog

#original
from text_uexp import TextUexp
import uexp_to_json, make_dualsub_mod, resize_subtitle_box

#---utils for tk---
def add_entry(frame, text='', row=0, col=0, width=60, sticky='w'):
    val = tk.StringVar()
    entry = ttk.Entry(
        frame,
        textvariable=val,
        width=width)
    entry.insert(tk.END, text)
    entry.grid(row=row, column=col, sticky=sticky)
    return val, entry

def add_text(frame, text, row=0, col=0, padding=(5,2), sticky='w'):
    label = ttk.Label(frame, text=text, padding=padding)
    label.grid(row=row, column=col, sticky=sticky)    
    return label

def add_button(frame, text, func, row=0, col=0, padding=(2,4), sticky='w'):
    val = tk.StringVar(frame)
    val.set(text)
    button = tk.Button(frame, textvariable=val, command=func)
    button.grid(row=row, column=col, sticky=sticky, padx=padding[0], pady=padding[1])
    return button

def add_combobox(frame, texts, row=0, col=0, width=10, sticky='w'):
    val = tk.StringVar()
    cb = ttk.Combobox(
        frame, textvariable=val, 
        values=texts, width=width,
        state='readonly')
    cb['values']=texts
    cb.current(0)
    cb.grid(row=row, column=col, sticky=sticky)
    return val, cb

def add_checkbox(frame, text, row=0, col=0, sticky='w'):
    boolean = tk.BooleanVar()
    cb=tk.Checkbutton(frame, variable=boolean, text=text)
    cb.grid(row=row, column=col, sticky=sticky)
    return boolean, cb

def add_num_valid_to_entry(entry, var, min, max):
    def validation(before, after):
        if len(after)==0:
            return True
        if not after.isdecimal():
            return False
        d=int(after)
        if d>=max:
            var.set(str(max))
        if d<=min:
            var.set(str(min))
        return True
    vcmd = (entry.register(validation), '%s', '%P')
    entry.configure(validate='key', validatecommand=vcmd)

def get_change_mode_func(frames, mode):
    def change_mode_func():
        frames[mode].tkraise()
    return change_mode_func

def get_open_url_func(url):
    def open_url_func():
        webbrowser.open(url, new=0, autoraise=True)
    return open_url_func

def get_file_func(val, file_types, initialdir):
    def file_func():
        if not os.path.exists(initialdir.get()):
            initialdir.set(os.getcwd())
        file = filedialog.askopenfilename(filetypes=file_types, initialdir=initialdir.get())
        if file!='':
            val.set(file)
            initialdir.set(os.path.dirname(file))
    return file_func

def check_file_exist(file, extention):
    if file=='' or file is None:
        messagebox.showinfo('File Not Found', 'You must specify a file name of .'+extention)
        return False
    if not os.path.exists(file) or not os.path.isfile(file):
        messagebox.showinfo('File Not Found', 'File not found. Check the file name.')
        return False
    if file.split('.')[-1]!=extention:
        messagebox.showinfo('Format Error', 'The file is not a .'+extention+' file')
        return False  
    return True

def ask_overwrite(file):
    q='yes'
    if os.path.exists(file):
        q=messagebox.askquestion('Overwrite?','"'+file+'" already exists.\r\nDo you want to overwrite it?', icon='warning')
    return q=='yes'


#---args for uexp_to_json.py---
class ConverterArgs:
    def __init__(self, uexp, json="", out_dir=""):
        self.uexp=uexp
        self.json=json
        self.out_dir=out_dir
        self.vorbose=False

#---args for make_dualsub_mod.py---
class DualsubArgs:
    def __init__(self, pak_dir, lang1, lang2, swap, all):
        self.pak_dir=pak_dir
        self.lang1=lang1
        self.lang2=lang2
        self.just_swap=swap
        self.all=all
        self.vorbose=False
        self.mod_name="Dual"*(not swap)+"Swap"*swap+"sub_"+lang1+"_"+lang2+"_all"*all
        self.save_as_json=False
        self.save_as_txt=False
        
#---args for resize_subtitle_box.py---
class WedgetArgs:
    def __init__(self, uexp, width, height):
        self.uexp=uexp
        self.width=width
        self.height=height

#---main app---
class App:
    def __init__(self):

        root = tk.Tk()
        root.title('FF7R Text Mod Tools '+'ver.'+TextUexp.VERSION+' by MatyaModding')
        root.minsize(340, 180)

        self.get_config()

        #make frames
        frames ={}
        frame_name = ['Export', 'Import', 'Dualsub', 'Wedget']
        frame_title = ['Export Text Data', 'Import Text Data', 'Make Dualsub', 'Resize Subtitle Wedget']
        frame_desc = ['Extracts text data from .uexp', 'Imports text data from .json to .uexp',\
                      'Merges (or swaps) subtitle data between 2 languages', 'Resizes subtitle text box']
        for title, name, desc in zip(frame_title, frame_name, frame_desc):
            frame = tk.Frame(root)
            frame.grid(row=0, column=0, sticky='nsew')
            header=tk.Frame(frame)
            header.grid(row=0,column=0,sticky='ew')
            label = add_text(header, title, padding=(5,2))
            label.config(font=('arial', 12))
            add_text(header, desc, row=1, padding=(5,2))
            body=tk.Frame(frame)
            body.grid(row=1,column=0,sticky='ew')

            if name==frame_name[0]:
                #frame for export mode
                add_text(body, '.uexp file', row=1, sticky='e')
                self.uexp,_ = add_entry(body, row=1, col=1, width=40)
                add_button(body, '...', get_file_func(self.uexp, [('asset file', '*.uexp')], self.uexp_dir), row=1, col=2)
                add_text(body, 'export as', row=2, sticky='e')
                self.extention,_ = add_combobox(body, ['.json', '.txt'], row=2, col=1, width=5)
                add_button(frame,name, self.export_text_data, row=2, sticky='e')

            if name==frame_name[1]:
                #frame for import mode
                add_text(body, '.uexp file', row=1, sticky='e')
                self.uexp_import,_ = add_entry(body, row=1, col=1, width=40)
                add_button(body, '...', get_file_func(self.uexp_import, [('asset file', '*.uexp')], self.uexp_dir), row=1, col=2)
                add_text(body, '.json file', row=2, sticky='e')
                self.json,_ = add_entry(body, row=2, col=1, width=40)
                add_button(body, '...', get_file_func(self.json, [('json file', '*.json')], self.json_dir), row=2, col=2)
                add_button(frame,name, self.import_text_data, row=3, sticky='e')

            if name==frame_name[2]:
                #frame for dualsub mode
                langlist=TextUexp.LANG_LIST
                add_text(body, 'Resource', row=1, sticky='e')
                self.pak,_ = add_entry(body, row=1, col=1, width=40)
                self.pak.set(self.pak_dir)
                add_button(body, '...', self.ask_pak_dir, row=1, col=2)
                add_text(body, 'lang1', row=2, sticky='e')
                self.lang1_var,_ = add_combobox(body, langlist, row=2, col=1, width=5)
                self.lang1_var.set(self.lang1)
                add_text(body, 'lang2', row=3, sticky='e')
                self.lang2_var,_ = add_combobox(body, langlist, row=3, col=1, width=5)
                self.lang2_var.set(self.lang2)
                footer=tk.Frame(frame)
                footer.grid(row=2, sticky='e')
                self.swapsub,_ = add_checkbox(footer, 'swap', col=0, sticky='e')
                self.all,_ = add_checkbox(footer, 'all text', col=1, sticky='e')
                add_button(footer,'Make Dualsub', self.make_dual_sub, col=2, sticky='e')

            if name==frame_name[3]:
                #frame for resize wedget mode
                add_text(body, 'Subtitle00.uexp', row=1, sticky='e')
                self.uexp_wedget,_ = add_entry(body, row=1, col=1, width=33)
                add_button(body, '...', get_file_func(self.uexp_wedget, [('Subtitle00.uexp', '*Subtitle00.uexp')], self.uexp_wedget_dir), row=1, col=2)
                add_text(body, 'Width (1~1920)', row=2, sticky='e')
                self.width, width_entry = add_entry(body, row=2, col=1, width=5)
                add_num_valid_to_entry(width_entry, self.width, 1, 1920)
                add_text(body, 'Height (1~1080)', row=3, sticky='e')
                self.height, height_entry = add_entry(body, row=3, col=1, width=5)
                add_num_valid_to_entry(height_entry, self.height, 1, 1080)
                footer=tk.Frame(frame)
                footer.grid(row=2, sticky='w')
                add_text(footer, 'preset', col=0, sticky='e')
                add_button(footer,'Vanilla', self.setSize(930, 210), col=1, sticky='w')
                add_button(footer,'Dualsub', self.setSize(1170, 260), col=2, sticky='w')
                add_button(footer,'Resize', self.resize_subtitle_wedget, col=6, sticky='ew')
                col_count,_ = footer.grid_size()
                for col in range(col_count):
                    footer.grid_columnconfigure(col, minsize=42)

            frames[name]=frame
        frames[frame_name[self.mode]].tkraise()

        menu = tk.Menu(root)

        #set mode menu
        menu_mode = tk.Menu(menu, tearoff=0)
        for label, name in zip(frame_title, frame_name):
            menu_mode.add_command(label=label, command=get_change_mode_func(frames, name))
        menu_mode.add_separator()
        menu_mode.add_command(label='Exit', command=self.on_closing)
        menu.add_cascade(label='Mode', menu=menu_mode)

        #set help menu
        menu_help = tk.Menu(menu, tearoff=0)
        help_label=['Tutorial', 'File List', 'Text Decoration', 'Report Issues']
        git_repo='https://github.com/matyalatte/FF7R_text_mod_tools'
        help_url=[git_repo+'/wiki/Text-Mod-Tutorial',
                git_repo+'/wiki/File-List',
                git_repo+'/wiki/Text-Decoration',
                git_repo+'/issues']
        for label, url in zip(help_label, help_url):
            menu_help.add_command(label=label, command=get_open_url_func(url))
        menu.add_cascade(label='Help', menu=menu_help)

        root.config(menu=menu)
        
        #set closing function
        root.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        self.root = root
    
    def run(self):
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel('Quit', 'Do you want to quit?'):
            self.root.destroy()

    def export_text_data(self):
        uexp = self.uexp.get()
        if not check_file_exist(uexp, 'uexp'):
            return
        
        out_dir = filedialog.askdirectory(initialdir=self.json_dir.get())
        if out_dir=='':
            return
        if not os.path.exists(out_dir):
            messagebox.showinfo('Folder Not Found', 'The folder you specified does not exist.')
            return
        self.json_dir.set(out_dir)
        self.mode=0
        self.save_config()
        args=ConverterArgs(uexp, out_dir=out_dir)
        extention=self.extention.get()
        new_file=os.path.join(out_dir,os.path.basename(uexp))[:-5]+extention
        if not ask_overwrite(new_file):
            return
        try:
            if extention==".json":
                uexp_to_json.uexp_to_json(args)
            else:
                uexp_to_json.uexp_to_txt(args)
            
            messagebox.showinfo('Done!', '"'+new_file+'" have been generated successfully.')
        except RuntimeError as e:
            messagebox.showerror('Export Error',e)
        except Exception as e:
            messagebox.showerror('Unexpected Error',e)

    def import_text_data(self):
        uexp = self.uexp_import.get()
        if not check_file_exist(uexp, 'uexp'):
            return
        json = self.json.get()
        if not check_file_exist(json, 'json'):
            return
        
        out_dir = filedialog.askdirectory(initialdir=self.new_uexp_dir.get())
        if out_dir=='':
            return
        if not os.path.exists(out_dir):
            messagebox.showinfo('Folder Not Found', 'The folder you specified does not exist.')
            return
        self.new_uexp_dir.set(out_dir)
        self.mode=1
        self.save_config()
        args=ConverterArgs(uexp, json=json, out_dir=out_dir)
        new_file=os.path.join(out_dir,os.path.basename(uexp))
        if not ask_overwrite(new_file):
            return
        try:
            uexp_to_json.json_to_uexp(args)
            messagebox.showinfo('Done!', '"'+new_file+'" have been generated successfully.')
        except RuntimeError as e:
            messagebox.showerror('Import Error',e)
        except Exception as e:
            messagebox.showerror('Unexpected Error',e)

    def make_dual_sub(self):
        lang1=self.lang1_var.get()
        lang2=self.lang2_var.get()
        if lang1 not in TextUexp.LANG_LIST:
            messagebox.showinfo('Unsupported Language', 'Unsupported language is specified as lang1.')
            return
        if lang2 not in TextUexp.LANG_LIST:
            messagebox.showinfo('Unsupported Language', 'Unsupported language is specified as lang2.')
            return
        if lang1==lang2:
            messagebox.showinfo('Same Language', 'lang1 and lang2 are the same.')
            return
        pak=self.pak.get()
        if not os.path.exists(pak):
            messagebox.showinfo('Folder Not Found', 'The pak folder you specified does not exist.')
            return
        self.lang1=lang1
        self.lang2=lang2
        self.pak_dir=pak
        self.mode=2
        self.save_config()
        swapsub = self.swapsub.get()
        all = self.all.get()
        args = DualsubArgs(pak, lang1, lang2, swapsub, all)

        if not ask_overwrite(args.mod_name):
            return
        try:
            make_dualsub_mod.make_dual_sub_mod(args)
            messagebox.showinfo('Done!', '"'+args.mod_name+'" have been generated successfully.')
        except RuntimeError as e:
            messagebox.showerror('Make Dualsub Error',e)
        except Exception as e:
            messagebox.showerror('Unexpected Error',e)
    
    def resize_subtitle_wedget(self):
        uexp = self.uexp_wedget.get()
        if not check_file_exist(uexp, 'uexp'):
            return

        width=self.width.get()
        height=self.height.get()
        if width=='' or height=='':
            messagebox.showinfo('Missing Arguments', 'You must specify the size of wedget.')
            return False

        self.uexp_wedget_dir.set(os.path.dirname(uexp))
        self.mode=3
        self.save_config()
        
        args=WedgetArgs(uexp, width, height)
        new_file=os.path.join(os.getcwd(), "new_Subtitle00.uexp")
        if not ask_overwrite(new_file):
            return
        try:
            resize_subtitle_box.resize_subtitle_box(args)           
            messagebox.showinfo('Done!', '"'+new_file+'" have been generated successfully.')
        except RuntimeError as e:
            messagebox.showerror('Export Error',e)
        except Exception as e:
            messagebox.showerror('Unexpected Error',e)

    config_file='gui.config'
    def get_config(self):
        self.uexp_dir=tk.StringVar()
        self.json_dir=tk.StringVar()
        self.new_uexp_dir = tk.StringVar()
        self.uexp_wedget_dir = tk.StringVar()
        try:
            with open(App.config_file, 'r', encoding="utf-8") as f:
                json_data = json.load(f)
                config = json_data["config"]

                for n in ["uexp_dir", "json_dir", "new_uexp_dir", "pak_dir", "uexp_wedget_dir"]:
                    if not ("uexp_dir" in config) or not os.path.exists(config[n]):
                        config[n]=os.getcwd()

                for n,v in zip(["lang1", "lang2", "mode"],["US", "JP", 0]):
                    if not n in config:
                        config[n]=v
                self.uexp_dir.set(config["uexp_dir"])
                self.json_dir.set(config["json_dir"])
                self.new_uexp_dir.set(config["new_uexp_dir"])
                self.uexp_wedget_dir.set(config["uexp_wedget_dir"])
                self.pak_dir=config["pak_dir"]
                self.lang1=config["lang1"]
                self.lang2=config["lang2"]
                self.mode=config["mode"]
        except Exception as e:
            print(e)
            print("Failed to load config. Default configuration will be applied.")
            self.uexp_dir.set(os.getcwd())
            self.json_dir.set(os.getcwd())
            self.new_uexp_dir.set(os.getcwd())
            self.uexp_wedget_dir.set(os.getcwd())
            self.pak_dir=os.getcwd()
            self.lang1="US"
            self.lang2="JP"
            self.mode=0


    def save_config(self):
        config={"uexp_dir":self.uexp_dir.get(), "json_dir":self.json_dir.get()}
        config["new_uexp_dir"]=self.new_uexp_dir.get()
        config["pak_dir"]=self.pak_dir
        config["uexp_wedget_dir"]=self.uexp_wedget_dir.get()
        config["lang1"]=self.lang1
        config["lang2"]=self.lang2
        config["mode"]=self.mode
        json_data={"config":config}
        meta = {"tool":"FF7R text mod tools", "version":TextUexp.VERSION}
        json_data["meta"]=meta
        with open(App.config_file, 'w', encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

    def ask_pak_dir(self):
        pak_dir = filedialog.askdirectory(initialdir=self.pak_dir)
        if pak_dir!='':
            self.pak_dir=pak_dir
            self.pak.set(pak_dir)

    def setSize(self, w,h):
        def func():
            self.width.set(str(w))
            self.height.set(str(h))
        return func

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uexp', default=None, help = "uexp")
    parser.add_argument('--vorbose', action='store_true')

    #for uexp to json
    parser.add_argument('--mode', default="uexp2json", help="uexp2json or json2uexp or uexp2txt or dualsub or resize")
    parser.add_argument('--json', default=None)
    parser.add_argument('--out_dir', default=None)
    
    
    #for dualsub
    parser.add_argument('--pak_dir', default=None, help = "where you unpaked .pak file.")
    parser.add_argument('--lang1', default=None, help = "BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US")
    parser.add_argument('--lang2', default=None, help = "BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US")
    parser.add_argument('--mod_name', default="dualsub_mod_l1_l2", help = "Folder's name for new mod")
    parser.add_argument('--save_as_json', action='store_true', help="Export subtitle data as json")
    parser.add_argument('--save_as_txt', action='store_true', help="Export subtitle data as txt")
    parser.add_argument('--just_swap', action='store_true', help="")
    parser.add_argument('--all', action='store_true', help="Edit all text data in the game")

    #for subtitle wedget
    parser.add_argument('--width', default=1170, help = "width of subtitle text box")
    parser.add_argument('--height', default=260, help = "height of subtitle text box")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    ver = TextUexp.VERSION
    print("FF7R Text Mod Tools ver "+ver+" by Matyalatte")
    args = get_args()
    if (args.uexp is None) and (args.pak_dir is None):
        print("mode: GUI")
        app = App()
        app.run()

    else:
        mode = args.mode
        if mode is None:
            raise RuntimeError("You missing an argument. (--mode)")
        print("mode: "+mode)
        if mode=="dualsub":
            m_list=["--pak_dir", "--lang1", "--lang2"]
            for arg, m in zip([args.pak_dir, args.lang1, args.lang2], m_list):
                if arg is None:
                    raise RuntimeError("You missing an argument. ("+m+")")
            make_dualsub_mod.make_dual_sub_mod(args)
        elif mode=="resize":
            if args.uexp is None:
                raise RuntimeError("You missing an argument. (--uexp)")
            resize_subtitle_box.resize_subtitle_box(args)
        else:
            if args.uexp is None:
                raise RuntimeError("You missing an argument. (--uexp)")
            if mode=="json2uexp":
                if args.json is None:
                    raise RuntimeError("You missing an argument. (--json)")
                uexp_to_json.json_to_uexp(args)
            elif mode=="uexp2json":
                uexp_to_json.uexp_to_json(args)
            elif mode=="uexp2txt":
                uexp_to_json.uexp_to_txt(args)
            else:
                raise RuntimeError("Unsupported mode. ("+mode+")")
            







    