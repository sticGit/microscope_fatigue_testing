
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import h5py
import numpy.linalg
import matplotlib
import sys

if __name__ == "__main__":
    print ("Loading data...")

    df = h5py.File(sys.argv[1], mode = "r")
    print("Data groups in this file:")
    for k, v in df.items():
        print("{}: {} items".format(k, len(v.keys())))
    try:
        data_group = df[sys.argv[2]] # should be fatigue_test%03d
    except:
        print("Picking latest group, no group specified")
        data_group = df.values()[-1]
    print("Using group {}".format(data_group.name))

    dset_names = data_group.keys()
    print(dset_names)

    N = len(dset_names)//4 # this is the number of out-and-backs we did
    first_move = data_group['data_cam_out00000']
    m = first_move.shape[0] # the number of data points in each move
    
    # let's combine the datasets
    cam_coords = np.empty((2*N*m, 2))
    stage_coords = np.empty_like(cam_coords)
    
    f, ax = plt.subplots(2,1, sharex=True)
    f2, ax2 = plt.subplots(1,1)
    xs = []
    for i in range(N-1): # ignore the last move, it may not have completed properly
        for d in ['out', 'back']:
            data_cam = data_group['data_cam_{}{:05d}'.format(d,i)]
            data_stage = data_group['data_stage_{}{:05d}'.format(d,i)]
            x = np.arange(m, dtype=np.int) + 2*i*m + (m if d=="back" else 0)
            rr = slice(np.min(x), np.max(x)+1)
            cam_coords[rr, :] = data_cam[:,:2]
            stage_coords[rr, :] = data_stage[:,:2]
            for j in range(2):
                ax[j].plot(x,data_cam[:,j])
            ax2.plot(data_cam[:,0], data_cam[:,1])
            
    plt.show()
