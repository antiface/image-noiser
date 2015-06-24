#!/usr/bin/env python3
import math
import numpy as np
from PIL import Image
from argparse import ArgumentParser

def add_noise(image, smoothing, distribution = None):
    """Get a copy image with added noise.

    Arguments:
    image -- the image to be copied
    smoothing -- a scaling factor to control for the amount of noise
    distribution -- Distribution of the noise.
    		    "gaussian" -> N(0,85); "uniform" -> Unif(-255,255)
    """
    imagecode = np.asarray(image)

    if distribution == 'gaussian':
        noise = np.random.normal(loc=0,scale=1/3,
                                 size=imagecode.shape)
    else:
        noise =  2 * np.random.random(imagecode.shape) - 1

    noisemask  = (256 * smoothing * noise)
    
    imagecode_noise = imagecode + noisemask
    imagecode_noise_clipped = np.clip(imagecode_noise, 0, 255)
    image_noise = Image.fromarray(
        imagecode_noise_clipped.astype('uint8'))
    return image_noise

def image_montage(imagelist, imgmode, max_cols):
    """ Concatenate a list of images in a new image.
    
    Arguments: 
    imagelist -- list of images to be concatenated
    imgmode   -- mode of the new image
    max_cols  -- number of images that can be horizontally aligned.
    """
    dimensions = [im.size for im in imagelist]
    width, height = (max(d) for d in zip(*dimensions))    

    n = len(imagelist)
    n_cols = min(max_cols,n)
    n_rows = math.ceil(n / n_cols)

    imgsize = (n_cols * width, n_rows * height)
    
    concat = Image.new(mode=imgmode,size = imgsize)
    for i,im in enumerate(imagelist):
        column = i % max_cols
        row   = i // max_cols
        concat.paste(im, (width*column, height*row))
    return concat

def main():
    MODE   = 'RGB'

    parser = ArgumentParser(description="Creates a series of copies of an image with added noise.")

    parser.add_argument('image', help= 'image to be noised.')

    parser.add_argument('-p','--prefix',default='',
                        help='prefix to add to noised images.')

    parser.add_argument('-t','--noisetype', default='uniform',
                        help='type of noise to be added.')

    parser.add_argument(
        '-s','--noisescale',
        default='0.1,0.3,0.5,0.7,0.9,1.1,1.3,1.5',
        help='value or list of values (comma separated) to \
        scale the noise.')

    parser.add_argument(
        '-m','--montage',action="store_true",
        help='concatenate all images instead of creating one \
        per noise mask.')
    
    args = parser.parse_args()

    scale = [float(f) for f in args.noisescale.split(',')]
    im_ref = Image.open(args.image)
    im_noising = [add_noise(im_ref, s, args.noisetype)
                      for s in scale]

    if args.montage:
        im_concat = image_montage(im_noising, MODE, 3)
        im_concat_small = im_concat.resize((600,800))
        im_concat_small.save('{}montage.jpg'.format(args.prefix))
    else:             
        for i, im in enumerate(im_noising):
            im.save('{}{}.jpg'.format(args.prefix,scale[i]))


if __name__ == '__main__':
    main()
