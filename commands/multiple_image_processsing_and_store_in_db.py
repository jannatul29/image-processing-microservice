import argparse
import os
import sys
import zipfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import concurrent.futures
import multiprocessing

from services.celery_worker import image_processing_task


class ImageDataStoring:
    def __init__(self):
        self.images_file_root = 'data/dynamic'
        self.task_ids = multiprocessing.Manager().list()
    
    def extract_zip(self, zip_path):
        """ Extracts ZIP file and returns a list of extracted TIFF files """
        self.images_path_root = 'data/dynamic'
        zip_filename = os.path.basename(zip_path)
        zip_name = os.path.splitext(zip_filename)[0]
        images_dir = f"{self.images_file_root}/{zip_name}"
        extracted_files = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(images_dir)
            for file in zip_ref.namelist():
                if file.endswith('.tiff') or file.endswith('.tif'):
                    extracted_files.append(os.path.join(images_dir, file))
        return extracted_files

    def image_processing_and_store(self, img):
        print("Processing images asynchronously...")
        task = image_processing_task.apply_async(args=[img])
        self.task_ids.append(task.id)
    
    def main(self, zip_file):
        """ Main function to process a ZIP file """
        if not os.path.exists(zip_file):
            print("Error: File does not exist.")
            return

        print(f"Extracting files from {zip_file}...")
        extracted_files = self.extract_zip(zip_file)
        
        if not extracted_files:
            print("No TIFF images found in ZIP.")
            return
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            results = executor.map(self.image_processing_and_store, extracted_files)
            try:
                for _ in results:
                    pass
            except Exception as error:
                print(str(error))
        
        print("Final Task IDs:", list(self.task_ids))  


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a ZIP file containing TIFF images.")
    parser.add_argument("--zipfile", type=str, help="Path to the ZIP file")
    args = parser.parse_args()

    image_data_storing_command = ImageDataStoring()
    image_data_storing_command.main(args.zipfile)
