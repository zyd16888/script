import os
import pymongo
import re

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
collection = db["your_collection_name"]

# Directory containing the files
base_dir = "V:\\"


def sanitize_filename(filename):
    # Remove or replace invalid characters
    return re.sub(r'[<>:"/\\|?*]', "", filename)


def find_matching_document(filename):
    # Remove file extension and "-C" suffix for search, but keep track of "-C"
    search_name = os.path.splitext(filename)[0]
    has_c_suffix = search_name.endswith("-C")
    search_name = re.sub(r"-C$", "", search_name)

    # Search in the database
    result = collection.find_one(
        {"Title": {"$regex": f"^{re.escape(search_name)}$", "$options": "i"}}
    )
    return result, has_c_suffix


def rename_files():
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.endswith(".mp4"):  # Adjust this if you have other file types
                old_path = os.path.join(root, filename)

                # Find matching document in MongoDB
                doc, has_c_suffix = find_matching_document(filename)

                if doc:
                    title = doc.get("Title", "")
                    if has_c_suffix:
                        title += "-C"
                    movie_name = doc.get("Movie Name", "")
                    actress = doc.get("Actress", "")

                    # Create the new filename
                    new_name = f"{title}-{movie_name}-{actress}"
                    new_name = sanitize_filename(new_name)
                    new_path = os.path.join(
                        root, new_name + os.path.splitext(filename)[1]
                    )

                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {old_path} -> {new_path}")
                    except Exception as e:
                        print(f"Error renaming {old_path}: {str(e)}")

                    # Rename the parent directory if it matches the old filename (without extension)
                    dir_name = os.path.basename(root)
                    if dir_name == os.path.splitext(filename)[0]:
                        old_dir_path = root
                        new_dir_path = os.path.join(os.path.dirname(root), new_name)
                        try:
                            os.rename(old_dir_path, new_dir_path)
                            print(
                                f"Renamed directory: {old_dir_path} -> {new_dir_path}"
                            )
                        except Exception as e:
                            print(f"Error renaming directory {old_dir_path}: {str(e)}")
                else:
                    print(f"No matching document found for: {filename}")


if __name__ == "__main__":
    rename_files()
