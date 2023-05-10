
import os

sub_path = "resources/rules/"

id_to_files = {}

for file in os.listdir(sub_path):
  if file.endswith(".yaml"):
    with open(sub_path + file, 'r') as f:
      line = f.readline().strip()
      uuid = line.split(":")[1].strip()
      if uuid in id_to_files.keys():
        msg = f"Duplicate key found for id={uuid}, file1={id_to_files[uuid]}, file2={file}"
        raise Exception(msg)
      id_to_files[uuid] = file
print(f"Successfully validated {id_to_files.size()} files for duplicate IDs")


