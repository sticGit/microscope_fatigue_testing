
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import h5py
import numpy.linalg
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
import sys
from os.path import basename, splitext
import argparse
from contextlib import contextmanager, closing

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse data from the fatigue test experiment.")
    parser.add_argument("filename", default="fatigue_tests.hdf5", nargs="?", help="Filename of the data file you are plotting")
    parser.add_argument("group_path", default="<latest>", nargs="?", help="The path of the data group you want to plot (defaults to the most recent).")
    parser.add_argument("--output_file", help="Filename for the output HDF5 file, defaults to the input filename plus _<group_path>_summary.h5.")
    parser.add_argument("--no_summary", action="store_true", help="Disable generating the summary file (HDF5 file with images stripped out)")
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
    
    # Save these plots as a PDF
    if "_summary" in args.filename:
        pdf_fname = splitext(args.filename)[0] + ".pdf"
    else:
        pdf_fname = splitext(args.filename)[0] + "_" + basename(data_group.name) + ".pdf"
    print("Saving PDF of plots to {}".format(pdf_fname))
    with PdfPages(pdf_fname) as pdf:
        pdf.savefig(f)
        pdf.savefig(f2)
   
    # Generate a "summary" HDF5 file without the images embedded every 100 moves, and containing only one group.
    if not args.no_summary:
        def basename(f):
            return f.split('/')[-1]
        if args.output_file is None:
            output_fname = splitext(args.filename)[0] + "_" + basename(data_group.name) + "_summary.h5"
        else:
            output_fname = args.output_file
        print("Saving just this dataset, with no images, to {}".format(output_fname))
        with closing(h5py.File(output_fname, mode="w")) as outfile:
            g = outfile.create_group(data_group.name)
            # copy the group attributes
            for k, v in data_group.attrs.items():
                g.attrs[k] = v
            for name, dset in data_group.items():
                if name.startswith("data_"):
                    g[name] = np.array(dset)
                    for k, v in dset.attrs.items():
                        g[name].attrs[k] = v
            g['template_image'] = np.array(data_group['template_image'])
    
    plt.show()
