def make_new_file(filename, content):
    with open(f"{filename}.go", "w") as f:
        f.write(content)


def read_new_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
        return content
