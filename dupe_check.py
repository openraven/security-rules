
import os

def extract_id(file):
  with open(sub_path + file, 'r') as f:
    lines = f.readlines()
    for line in lines:
      line = line.strip().split(":")
      if len(line) == 2 and line[0].strip() == "id":
        return line[1]
  return None


print(f"Initializing in {os.getcwd()}")
sub_path = "resources/rules/"
id_to_files = {}

for file in os.listdir(sub_path):
  if file.endswith(".yaml"):
    print(f"Processing {file}")
    uuid = extract_id(file)
    if uuid is None:
      print(f"Couldn't process {file}, ignoring.")
    else :  
      if uuid in id_to_files.keys():
        msg = f"Duplicate key found for id={uuid}, file1={id_to_files[uuid]}, file2={file}"
        raise Exception(msg)
      id_to_files[uuid] = file
print(f"Successfully validated {len(id_to_files)} files for duplicate IDs")


