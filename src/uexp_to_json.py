import os,argparse
import file_util as util
from text_uexp import TextUexp

ver = TextUexp.VERSION

def get_args():
    parser = argparse.ArgumentParser() 
    parser.add_argument('uexp', help = "")
    parser.add_argument('--mode', default="uexp2json", help="uexp2json or json2uexp or uexp2txt")
    parser.add_argument('--json', default=None)
    parser.add_argument('--out_dir', default=None)
    parser.add_argument('--vorbose', action='store_true')

    args = parser.parse_args()
    return args

if __name__=="__main__":
    
    #Get args
    args=get_args()

    if args.vorbose:
        print("FF7R Text Mod Tools ver "+ver+" by Matyalatte")

    print("uexp: "+args.uexp)

    if args.vorbose:
        print("--mode: "+args.mode)
        print("--out_dir: "+args.out_dir)
    
    def uexp_to_json(args):
        uexp_file = args.uexp
        out_dir = args.out_dir
        if out_dir is None:
            out_dir="json"
        
        #Load uexp
        uexp = TextUexp(uexp_file, args.vorbose)

        #Save as json
        util.mkdir(out_dir)
        uexp.save_as_json(os.path.join(out_dir, os.path.basename(uexp_file)[:-4]+"json"))

    def json_to_uexp(args):
        if args.vorbose:
            print("--json: "+args.json)

        if args.json is None:
            raise RuntimeError("Specify a json file by '--json' argument.")

        uexp_file = args.uexp
        json_file = args.json
        out_dir = args.out_dir
        if out_dir is None:
            out_dir="new_uexp"
        
        #Load uexp
        uexp = TextUexp(uexp_file, args.vorbose)

        #Swap subtitle text with json
        uexp.swap_with_json(json_file)

        #Save as uexp
        util.mkdir(out_dir)
        uexp.save_as_uexp(os.path.join(out_dir, os.path.basename(uexp_file)))

    def uexp_to_txt(args):
        uexp_file = args.uexp
        out_dir = args.out_dir
        if out_dir is None:
            out_dir="txt"

        uexp = TextUexp(uexp_file, args.vorbose)

        #Save as txt
        util.mkdir(out_dir)
        uexp.save_as_txt(os.path.join(out_dir, os.path.basename(uexp_file)[:-4]+"txt"))

    if args.mode=="uexp2json":
        uexp_to_json(args)
    elif args.mode=="json2uexp":
        json_to_uexp(args)
    elif args.mode=="uexp2txt":
        uexp_to_txt(args)
    else:
        raise RuntimeError("Unsupported mode. ({})".format(args.mode))

    print("Done!")

