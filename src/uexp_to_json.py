import os,argparse
import file_util as util
from text_uexp import TextUexp

def get_args():
    parser = argparse.ArgumentParser() 
    parser.add_argument('uexp', help = "")
    parser.add_argument('--out_dir', default="json")
    parser.add_argument('--vorbose', action='store_true')
    args = parser.parse_args()
    return args

if __name__=="__main__":
    
    #Get args
    args=get_args()
    file = args.uexp
    out_dir = args.out_dir
    
    #Load uexp
    uexp = TextUexp(file, args.vorbose)

    #Save as json
    util.mkdir(out_dir)
    uexp.save_as_json(os.path.join(out_dir, os.path.basename(file)[:-4]+".json"))

