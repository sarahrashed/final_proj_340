import zipfile
import os

zip_path = "roboflow-ingredients-dataset.zip"
extract_path = "ingredients_dataset"

# Extract if not already done
if not os.path.exists(extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print("✅ Extracted to", extract_path)
else:
    pass

