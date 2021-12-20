import os,argparse
import file_util as util
from text_uexp import TextUexp

def get_args():
    parser = argparse.ArgumentParser() 
    parser.add_argument('uexp', help = "")
    parser.add_argument('json')
    parser.add_argument('--out_dir', default="new_uexp")
    parser.add_argument('--vorbose', action='store_true')
    args = parser.parse_args()
    return args

if __name__=="__main__":
    
    #Get args
    args=get_args()
    uexp_file = args.uexp
    json_file = args.json
    out_dir = args.out_dir
    
    #Load uexp
    uexp = TextUexp(uexp_file, args.vorbose)

    #Swap subtitle text with json
    uexp.swap_with_json(json_file)

    #Save as uexp
    util.mkdir(out_dir)
    uexp.save_as_uexp(os.path.join(out_dir, os.path.basename(uexp_file)))

