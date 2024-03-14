import os
from glob import glob
import numpy as np
import pandas as pd

import dicom


def init(shuffle=False, seed=None):
    DATASETPATH = os.environ["DATASETPATH"]
    DS_INFO_FILE = os.environ["DATASET"]

    ds_df = pd.read_csv(os.path.join(DATASETPATH, DS_INFO_FILE))

    # reading images
    SUBDIR_IMAGES_PATTERN = None
    if "SUBDIR_IMAGES_PATTERN" in os.environ:
        SUBDIR_IMAGES_PATTERN = os.environ["SUBDIR_IMAGES_PATTERN"]
        SUBDIR_IMAGES_PATTERN = SUBDIR_IMAGES_PATTERN.split(",")
        all_image_paths = {
            os.path.basename(x): x
            for x in glob(os.path.join(DATASETPATH, *SUBDIR_IMAGES_PATTERN))
        }
        print(
            "Loaded dataset and images paths\nScans found:",
            len(all_image_paths),
            ", Total Headers",
            ds_df.shape[0],
        )

        if seed is not None:
            np.random.seed(seed)

        if shuffle:
            indexes = np.arange(len(ds_df))
            np.random.shuffle(indexes)
            ds_df_shuffled = ds_df.iloc[indexes].reset_index(drop=True)
            ds_df = ds_df_shuffled

        return ds_df, all_image_paths
    return None, None
