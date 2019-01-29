
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import h5py
import numpy.linalg
import matplotlib
import sys
import argparse
from contextlib import contextmanager, closing

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse data from the fatigue test experiment.")
    parser.add_argument("filename", default="fatigue_tests.hdf5", nargs="?")
    parser.add_argument("group_path", default="<latest>", nargs="?")
    parser.add_argument("--output_file")
    args = parser.parse_args()
    print ("Loading data from {}...".format(args.filename))
    df = h5py.File(args.filename, mode = "r")
    print("Data groups in this file:")
    for k, v in df.items():
        print("{}: {} items".format(k, len(v.keys())))
    try:
        assert args.group_path != "<latest>"
        data_group = df[args.group_path] # should be fatigue_test%03d
    except:
        print("Picking latest group, no group specified")
        data_group = df.values()[-1]
    print("Using group {}".format(data_group.name))


    dset_names = data_group.keys()
#    print(dset_names)
    N = len([d for d in dset_names if d.startswith("data_cam")]) # this is the number of moves we did
    print("There were {} datasets, {} started with data_cam.".format(len(dset_names), N))

    first_move = data_group['data_cam00000']
    m = first_move.shape[0] # the number of data points in each move
    
    # let's combine the datasets
    cam_coords = np.empty((N*m, 2))
    stage_coords = np.empty_like(cam_coords)
    
    f, ax = plt.subplots(2,1, sharex=True)
    f2, ax2 = plt.subplots(1,1)
    xs = []
    for i in range(N):
        data_cam = data_group['data_cam{:05d}'.format(i)]
        data_stage = data_group['data_stage{:05d}'.format(i)]
        x = np.arange(m, dtype=np.int) + i*m
        rr = slice(np.min(x), np.max(x)+1)
        cam_coords[rr, :] = data_cam[:,:2]
        stage_coords[rr, :] = data_stage[:,:2]
        for j in range(2):
            ax[j].plot(x,data_cam[:,j])
        ax2.plot(data_cam[:,0], data_cam[:,1])
    ax2.set_aspect(1)
    
    def basename(f):
        return f.split('/')[-1]
    output_fname = args.filename + "_" + basename(data_group.name) + "_summary.hdf5" if args.output_file is None else args.output_file
    with closing(h5py.File(output_fname, mode="w")) as outfile:
        g = outfile.create_group(data_group.name)
        # copy the group attributes
        for k, v in data_group.attrs.items():
            g.attrs[k] = v
        for name, dset in g.items():
            if name.startswith("data_"):
                outfile[dset.name] = np.array(dset)
                for k, v in dset.attrs.items():
                    outfile[dset.name].attrs[k] = v
        g['template_image'] = np.array(data_group['template_image'])
            
    plt.show()
