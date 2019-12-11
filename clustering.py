from skimage.io import imread
from matplotlib import pyplot as plt
import numpy as np
import skimage
from sklearn.cluster import KMeans

from skimage import io

def clusterImage(img, clusters_n, init_n, tolerance):
    img = io.imread(img) 
    shape=img.shape
    img_float=skimage.img_as_float(img)
    uniq=np.unique(img, axis=0)
    print(len(uniq), ' unique colors')
    if len(uniq) < clusters_n:
        return None
        
    r=img_float[:,:,0]
    g=img_float[:,:,1]
    b=img_float[:,:,2]
    r=np.ravel(r)
    g=np.ravel(g)
    b=np.ravel(b)
    data=np.vstack((r,g,b)).T

    result=KMeans(n_clusters=clusters_n, verbose=True, n_init=init_n,tol=tolerance).fit(data)

    palette=result.cluster_centers_.reshape(-1,clusters_n,3)

    labels=result.labels_.reshape(shape[0],shape[1])
    img_new=img_float.copy()
    for x in range(0,shape[0]):
        for y in range(0,shape[1]):
            img_new[x,y,:]=palette[:,labels[x,y],:]
    return img_new
