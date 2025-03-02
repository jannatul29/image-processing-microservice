import numpy as np
import dask.array as da
import tifffile as tiff
from sklearn.decomposition import IncrementalPCA
from skimage.filters import threshold_otsu
from skimage.measure import label
from database.setup import get_db
from database.models import Images
import os

class ImageProcessor:
    def __init__(self, filepath: str, chunk_size=(1, 1, 256, 256, 1)):
        """Load a 5D image using chunked processing."""
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.image = self.load_image()

        if len(self.image.shape) != 5:
            raise ValueError("Image must have 5 dimensions (T, Z, Y, X, C).")
    
    def get_filename(self):
        return self.filepath.split('/')[-1]
    
    def load_image(self):
        try:
            if os.path.exists(self.filepath):
                return da.from_array(tiff.imread(self.filepath), chunks=self.chunk_size)
            else:
                return self.retrieve_dask_array()
        except Exception as error:
            print(error)
            return da.from_array(np.random.rand(1000, 1000), chunks=(250, 250))

    def get_metadata(self):
        """Retrieve image meta_data without loading full data."""
        try:
            t, z, y, x, c = self.image.shape
            return {"Time": t, "Depth": z, "Height": y, "Width": x, "Channels": c}
        except Exception as error:
            print(error)
            return {}

    def extract_slice(self, time: int, z: int, channel: int):
        """Extract a slice from the image using chunked reads."""
        return self.image[time, z, :, :, channel].compute()  # Load only the required part

    def compute_statistics(self):
        """Compute mean, std, min, max per channel using Dask."""
        stats = {}
        for i in range(self.image.shape[-1]):
            channel_data = self.image[:, :, :, :, i]
            stats[f"channel_{i}"] = {
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

    def get_image_attributes(self):
        filename = self.get_filename()
        dask_array = self.load_image()
        numpy_array = dask_array.compute()
        binary_data = numpy_array.tobytes()
        shape = list(numpy_array.shape),  # Convert tuple to list for JSON storage
        dtype = str(numpy_array.dtype)
        image_attr = {"shape": shape, "dtype": dtype}
        meta_data = self.get_metadata()
        # analysis_result = self.apply_pca()
        # return {"filename": filename, "image": binary_data, "metadata": meta_data, "analysis_result": analysis_result}
        return {"filename": filename, "image": binary_data, "metadata": meta_data, "image_attr": image_attr}
    
    def retrieve_dask_array(self):
        # Retrieve the binary data and metadata (shape, dtype) from the database
        db_session = next(get_db())
        stored_data = db_session.query(Images).filter_by(filename=self.filepath).first()
        if stored_data:
            # Validate metadata fields
            metadata = stored_data.image_attr
            if not metadata or "shape" not in metadata or "dtype" not in metadata:
                return None  # Metadata is missing or incomplete
            
            shape = tuple(metadata["shape"][0])  # JSON stores lists, so no need for string conversion
            dtype = np.dtype(metadata["dtype"])  # Ensure dtype is correctly reconstructed
            # Convert binary data back to a NumPy array
            numpy_array = np.frombuffer(stored_data.image, dtype=dtype).reshape(shape)

            # Convert to Dask array with the stored chunk size
            dask_array = da.from_array(numpy_array, chunks=self.chunk_size)

            return dask_array
        return da.from_array(np.random.rand(1000, 1000), chunks=(250, 250))
