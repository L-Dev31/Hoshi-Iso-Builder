import os
import shutil

def debug_log(message):
    print(f"[FILE_OPS DEBUG] {message}")

def get_path_str(path):
    if type(path) != str:
        return ""
    rtn_str = ""
    while path != "":
        if path[0] in "/\\":
            rtn_str += '/'
            while len(path) > 0 and path[0] in "/\\":
                path = path[1:]
        if len(path) > 0:
            rtn_str += path[0]
        path = path[1:]
    if rtn_str[-1] == '/':
        rtn_str = rtn_str[:-1]
    return rtn_str

def f_exists(path):
    path = get_path_str(path)
    debug_log(f"Checking existence: {path}")
    return os.path.exists(path)

def is_file(path):
    path = get_path_str(path)
    debug_log(f"Checking if file: {path}")
    return os.path.isfile(path)

def is_folder(path):
    path = get_path_str(path)
    debug_log(f"Checking if folder: {path}")
    return os.path.isdir(path)

def get_file_name(path):
    if type(path) != str:
        return None
    path = get_path_str(path)
    if f_exists(path):
        path = os.path.abspath(path)
    string = ""
    for i in range(len(path) - 1, -1, -1):
        if path[i] == '/':
            for j in range(i + 1, len(path)):
                string += path[j]
            break
    return string

def get_base_path(path, is_file):
    if (type(path) != str) or (type(is_file) != bool):
        return None
    path = get_path_str(path)
    if f_exists(path):
        path = get_path_str(os.path.abspath(path))
    if is_file:
        while path != "":
            if path[-1] == '/':
                path = path[:-1]
                break
            path = path[:-1]
    return path

def get_base_folder_name(path, is_file, folder_as_file):
    if (type(path) != str) or (type(is_file) != bool) or (type(folder_as_file) != bool):
        return None
    path = get_path_str(path)
    if (is_file) or (is_file == False and folder_as_file):
        return get_file_name(get_base_path(path, True))
    return get_file_name(get_base_path(path, False))

def cp_file(src, dest):
    debug_log(f"Copying: {src} -> {dest}")
    if (f_exists(src) == False) or (is_file(src) == False):
        return False
    if f_exists(dest) == False:
        base_path = get_base_path(dest, True)
        if f_exists(base_path) == False:
            os.makedirs(base_path)
        shutil.copy(src, base_path + "/" + get_file_name(dest))
    elif f_exists(dest) == True and is_file(dest):
        base_path = get_base_path(dest, True)
        os.remove(dest)
        shutil.copy(src, base_path + "/" + get_file_name(dest))
    elif f_exists(dest) == True and is_folder(dest):
        shutil.copy(src, dest + "/" + get_file_name(src))
    return True

def list_folder_tree(src):
    if type(src) != str or f_exists(src) == False:
        return []
    f_list = [src]
    tmp_list = []
    while True:
        tmp_list = []
        for f in f_list:
            if f not in tmp_list:
                tmp_list.append(f)
            if is_folder(f):
                for int_f in os.listdir(f):
                    if (f + "/" + int_f) not in tmp_list:
                        tmp_list.append(f + "/" + int_f)
        if f_list == tmp_list:
            break
        f_list = tmp_list
    return f_list

def cp_folder(src, dest, treat_as_file):
    debug_log(f"Copying folder: {src} -> {dest} (treat_as_file={treat_as_file})")
    if (f_exists(src) == False) or (is_folder(src) == False) or (type(dest) != str) or (type(treat_as_file) != bool):
        return False
    if f_exists(dest) == False:
        os.makedirs(dest)
    if treat_as_file:
        dest = dest + "/" + get_base_folder_name(src, False)
        if f_exists(dest) == False:
            os.makedirs(dest)
    f_list = list_folder_tree(src)
    for f in f_list:
        dest_f_path = dest + "/" + f.replace(src, "")
        if is_file(f):
            cp_file(f, dest_f_path)
        elif is_folder(f) and (is_folder(dest_f_path) == False):
            os.makedirs(dest_f_path)
    return True

def rm_file(path):
    debug_log(f"Deleting file: {path}")
    if type(path) != str or f_exists(path) == False or is_file(path) == False:
        debug_log(f"File not found [skip]: {path}")
        return  # On ignore et on continue
    try:
        os.remove(path)
        debug_log(f"File deleted: {path}")
    except Exception as e:
        debug_log(f"Error deleting file: {str(e)}")

def rm_folder(path):
    debug_log(f"Deleting folder: {path}")
    if type(path) != str or f_exists(path) == False or is_folder(path) == False:
        debug_log(f"Folder not found [skip]: {path}")
        return  # On ignore et on continue
    try:
        shutil.rmtree(path)
        debug_log(f"Folder deleted: {path}")
    except Exception as e:
        debug_log(f"Error deleting folder: {str(e)}")

def get_file_size(path):
    debug_log(f"Getting file size: {path}")
    if not f_exists(path):
        debug_log(f"File not found: {path}")
        raise FileNotFoundError(f"The specified file was not found: {path}")
    if not is_file(path):
        debug_log(f"Not a file: {path}")
        raise ValueError(f"The specified path is not a file: {path}")
    try:
        size = os.path.getsize(get_path_str(path))
        debug_log(f"File size: {size} bytes")
        return size
    except Exception as e:
        debug_log(f"Error getting file size: {str(e)}")
        raise