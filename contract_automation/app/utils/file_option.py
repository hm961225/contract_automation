def file_save(path, name, file_type, content):
    with open(f"{path}{name}.{file_type}", "w") as f:
        f.write(content)

def read_new_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
        return content