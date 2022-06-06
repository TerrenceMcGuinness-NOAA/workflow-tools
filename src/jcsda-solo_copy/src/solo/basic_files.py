# --------------------------------------------------------------------------------
# Author: Claude Gibert
#
# --------------------------------------------------------------------------------
import os
import yaml

"""
    Some pretty basic functions on files  not to be undermined, they enable the programmer to write cleaner code.
"""


def clean_save(filename, data):
    """
        Creates a temporary file and saves the data into it,
        then renames the temporary file to filename. This is
        clean in a system where directories are being watched
        and files are processed when found.
    """
    f = open('%s.tmp' % filename, 'w')
    f.write(data)
    f.close()
    os.rename('%s.tmp' % filename, filename)


def directory_list(path, extension=None):
    """
        Returns list of file names in a directory. If extension is specified,
        only files with that extensions are returned.

        :param path: absolute or relative path to the directory
        :param extension: file name extension (without the '.')
        :return: a list of file names (without the path).
    """
    result = []
    if os.path.exists(path):
        files = os.listdir(path)
        if extension is None:
            result = files
        else:
            for file in files:
                file_list = file.split('.')
                if file_list[-1] == extension:
                    result.append(file)
    return result


def mkdir(directory):
    """
        Creates a directory without failing if the directory exists.
        :param directory: path to directory
        :return:
    """
    try:
        os.makedirs(directory)
    except OSError:
        pass


def clean_path(path):
    """
        get rid of multiple / together in a path
    """
    return '/'.join([x for x in path.split('/') if len(x)])


class FileWatcher(object):
    """
    Watches a file and when being polled, returns True if the file was
    modified since the object was created.
    """
    def __init__(self, file):
        self.file = file
        self.latest = os.stat(file).st_mtime

    def __call__(self):
        current = os.stat(self.file).st_mtime
        if current != self.latest:
            self.latest = current
            return True
        return False


class FileBrowser(object):
    def __init__(self, path, extension=None):
        self._path = path
        self._extension = extension

    def __call__(self, visitor):
        files = directory_list(self._path, self._extension)
        for filename in files:
            full_path = '%s/%s' % (self._path, filename)
            visitor(self, full_path, filename)

    @staticmethod
    def delete_file(full_path):
        os.unlink(full_path)

    @staticmethod
    def move_file(full_path, destination):
        os.rename(full_path, destination)


def tree(path):
    """
        Recursively visits path. Returns a tuple with three elements:
        path (argument to the function), relative path, filename
        To have the full_path:
        for root, path, filename in tree(root):
            full_path = os.path.join(root, path, filename)
    """
    for root, dirs, files in os.walk(path):
        if len(files):
            for file in files:
                r = root.replace(path, '', 1)
                if len(r) and r[0] == '/':
                    r = r[1:]
                yield path, r, file


def find_in_tree(root, file_name):
    for root, path, file in tree(root):
        full_path = os.path.join(root, path, file)
        filename = os.path.basename(full_path)
        match = file_name.replace('*', '')
        if filename.find(match) != -1:
            yield full_path


def free_space_fs(pathname):
    """
        Get the free space of the filesystem containing pathname
    """
    stat = os.statvfs(pathname)
    # use f_bfree for superuser, or f_bavail if filesystem
    # has reserved space for superuser
    return stat.f_bfree * stat.f_bsize


def find_config_dir(application):
    directory = os.path.join(user_home_directory(), f'.{application}')
    if not os.path.exists(directory):
        directory = os.path.join('/etc', application)
        if not os.path.exists(directory):
            raise FileNotFoundError(f'Cannot find configuration directory for {application}')
    return directory


def read_yaml_config(application, name):
    config_dir = find_config_dir(application)
    with open(os.path.join(config_dir, name)) as f:
        config = yaml.load(f, Loader=yaml.BaseLoader)
    return config


def user_home_directory():
    return os.path.expanduser('~')


def name_extension(path):
    parts = path.split('.')
    if len(parts) > 1:
        return '.'.join(parts[:-1]), parts[-1]
    return path, ''