
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import h5py
import numpy.linalg
import matplotlib

if __name__ == "__main__":
    print ("Loading data...")

    df = h5py.File("fatigue_tests.hdf5", mode = "r")
    data_group = df.values()[-1] # should be fatigue_test%03d
    dset_names = data_group.keys()
    print(dset_names)

    f, ax = plt.subplots(2,1)

    for i in range(len(dset_names)//4):
        for d in ['out', 'back']:
            data_cam = data_group['data_cam_{}{:05d}'.format(d,i)]
            data_stage = data_group['data_stage_{}{:05d}'.format(d,i)]
            N = data_cam.shape[0]
            x = np.arange(N) + 2*i*N
            if d == 'back':
                x += N
            ax[0].plot(x,data_cam[:,0])
            ax[1].plot(x,data_stage[:,0])
            
    plt.show()
