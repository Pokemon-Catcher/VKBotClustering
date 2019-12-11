import clustering
import config as cfg
import argparse
import os
from skimage import io

def parse_args():
    parser = argparse.ArgumentParser()  # Для параметров
    parser.add_argument('--n_clusters', type=int, default=cfg.DEFAULT_N_CLUSTERS)
    parser.add_argument('--image', type=str, default=cfg.DEFAULT_IMAGE)
    parser.add_argument('--name', type=str, default=cfg.DEFAULT_NAME)
    return parser.parse_args()
    
params = parse_args()
img = clustering.clusterImage(params.image, params.n_clusters, cfg.CLUSTERING_N_INIT, cfg.CLUSTERING_TOLERANCE)
if img is not None:
    io.imsave('../{}.png'.format(params.name), img)
else:
    os.remove('../{}.png'.format(params.name))
    
