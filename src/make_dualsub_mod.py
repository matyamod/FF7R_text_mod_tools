import os,argparse
import file_util as util
from text_uexp import TextUexp
from copy import deepcopy

ver = TextUexp.VERSION

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('pak_dir', help = "where you unpaked .pak file.")
    parser.add_argument('lang1', help = "BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US")
    parser.add_argument('lang2', help = "BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US")
    
    parser.add_argument('--mod_name', default="dualsub_mod_l1_l2", help = "Folder's name for new mod")
    parser.add_argument('--save_as_json', action='store_true', help="Export subtitle data as json")
    parser.add_argument('--save_as_txt', action='store_true', help="Export subtitle data as txt")
    parser.add_argument('--vorbose', action='store_true', help="")
    parser.add_argument('--just_swap', action='store_true', help="")
    parser.add_argument('--all', action='store_true', help="Edit all text data in the game")

    #parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    return args

def make_dual_sub_mod(args):
    pak_dir = args.pak_dir
    lang1 = args.lang1
    lang2 = args.lang2
    just_swap = args.just_swap
    print("lang1: "+args.lang1)
    print("lang2: "+args.lang2)
    
    #Check language
    if lang1==lang2:
        raise RuntimeError("lang1 and lang2 are the same.")

    LANG_LIST = ["BR", "CN", "DE", "ES", "FR", "IT", "JP", "KR", "MX", "TW", "US"]
    if lang1 not in LANG_LIST:
        raise RuntimeError(lang1+" is Not supported. Select another language.")
    if lang2 not in LANG_LIST:
        raise RuntimeError(lang2+" is Not supported. Select another language.")

    mod_name = args.mod_name
    if mod_name=="dualsub_mod_l1_l2":
        mod_name="Dual"*(not just_swap)+"Swap"*just_swap+"sub_"+lang1+"_"+lang2+"_all"*args.all

    print("mod name: "+mod_name)

    TEXT_DIR = "End/Content/GameContents/Text"

    lang1_dir = os.path.join(pak_dir,TEXT_DIR, lang1)
    lang2_dir = os.path.join(pak_dir,TEXT_DIR, lang2)

    def make_dualsub(uexp, lang, text_object_list):
        #Merge subtitles
        uexp.merge_text(text_object_list, just_swap=args.just_swap, mod_all=args.all, reject_similar_word=True)

        #Export subtitle data as json
        if args.save_as_json:
            uexp.save_as_json("json/"+lang+"/"+f[:-4]+".json")

        #Export subtitle data as json
        if args.save_as_txt:
            uexp.save_as_txt("txt/"+lang+"/"+f[:-4]+".txt")

        #Make a mod folder
        out_dir = os.path.join(mod_name, TEXT_DIR, lang)
        util.mkdir(out_dir)

        #Save as uexp and uasset
        uexp.save_as_uexp(os.path.join(out_dir, f))

    file_list = util.get_filelist(lang1_dir, extention="uexp")
    for f in file_list:
        print(f)

        #Load uexp
        uexp_lang1 = TextUexp(os.path.join(lang1_dir, f), args.vorbose)
        uexp_lang2 = TextUexp(os.path.join(lang2_dir, f), args.vorbose)
        lang1_text_object_list = deepcopy(uexp_lang1.text_object_list)
        lang2_text_object_list = deepcopy(uexp_lang2.text_object_list)
        
        if args.save_as_json:
            util.mkdir("json/"+lang1)
            util.mkdir("json/"+lang2)

        if args.save_as_txt:
            util.mkdir("txt/"+lang1)
            util.mkdir("txt/"+lang2)

        make_dualsub(uexp_lang1, lang1, lang2_text_object_list)
        make_dualsub(uexp_lang2, lang2, lang1_text_object_list)


if __name__=="__main__":
    print("FF7R Text Mod Tools ver "+ver+" by Matyalatte")

    #Get args
    args=get_args()

    make_dual_sub_mod(args)

    print("Done!")

