import os, struct, argparse
import file_util as util

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('uexp', help = "Subtitle00.uexp")
    parser.add_argument('--width', default=1170, help = "width of subtitle text box")
    parser.add_argument('--height', default=260, help = "height of subtitle text box")
    args = parser.parse_args()
    return args

def resize_subtitle_box(args):
    uexp = args.uexp
    if os.path.basename(uexp)!="Subtitle00.uexp":
        raise RuntimeError("Not 'Subtitle00.uexp'")

    width = args.width #vanilla:930, dualsub mod:1170
    height = args.height #vanilla:210, dualsub mod:260

    id = [344, 348, 456, 460, 722, 821]
    val = [width, height, width, height, width, width]

    #int -> float -> hex
    for i in range(len(val)):
        v = val[i]
        v = float(v)
        v = struct.pack('<f', v)
        val[i]=v

    #load data
    bin = util.read_binary(uexp)

    #swap data (bin[i:i+4]=v)
    new_bin = open("new_"+os.path.basename(uexp), "wb")
    oi=0
    for i, v in zip(id, val):
        new_bin.write(bin[oi:i])
        new_bin.write(v)
        oi=i+4
    new_bin.write(bin[oi:])
    new_bin.close()

if __name__=="__main__":
    args = get_args()
    resize_subtitle_box(args)
    print("Done!")
