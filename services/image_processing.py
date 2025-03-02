import numpy as np
import dask.array as da
import tifffile as tiff
from sklearn.decomposition import IncrementalPCA
from skimage.filters import threshold_otsu
from skimage.measure import label

class ImageProcessor:
    def __init__(self, filepath: str, chunk_size=(1, 1, 256, 256, 1)):
        """Load a 5D image using chunked processing."""
        self.filepath = filepath
        self.image = da.from_array(tiff.imread(filepath), chunks=chunk_size)

        if len(self.image.shape) != 5:
            raise ValueError("Image must have 5 dimensions (T, Z, Y, X, C).")

    def get_metadata(self):
        """Retrieve image metadata without loading full data."""
        t, z, y, x, c = self.image.shape
        return {"Time": t, "Depth": z, "Height": y, "Width": x, "Channels": c}

    def extract_slice(self, time: int, z: int, channel: int):
        """Extract a slice from the image using chunked reads."""
        return self.image[time, z, :, :, channel].compute()  # Load only the required part

    def compute_statistics(self):
        """Compute mean, std, min, max per channel using Dask."""
        stats = {}
        for i in range(self.image.shape[-1]):
            channel_data = self.image[:, :, :, :, i]
            stats[f"Channel {i}"] = {
                "mean": float(channel_data.mean().compute()),
                "std": float(channel_data.std().compute()),
                "min": float(channel_data.min().compute()),
                "max": float(channel_data.max().compute()),
            }
        return stats

    def apply_pca(self, n_components=3, batch_size=100000):
        """Perform PCA using incremental batch processing."""
        t, z, y, x, c = self.image.shape
        reshaped = self.image.reshape(-1, c)  # Convert to (pixels, channels)

        if c < n_components:
            raise ValueError(f"n_components ({n_components}) cannot exceed channels ({c}).")

        ipca = IncrementalPCA(n_components=n_components, batch_size=batch_size)
        for chunk in reshaped.to_delayed():
            ipca.partial_fit(chunk.compute())

        transformed = ipca.transform(reshaped.compute())
        return transformed.reshape(t, z, y, x, n_components)

    def apply_segmentation(self, time: int, z: int, channel: int):
        """Apply segmentation in chunks using Otsu’s thresholding."""
        slice_data = self.extract_slice(time, z, channel)
        threshold = threshold_otsu(slice_data)
        segmented = label(slice_data > threshold)
        return segmented
