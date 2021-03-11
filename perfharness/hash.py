import hashlib

class Hash:
    def __init__(self, data=None):
        self.hasher = hashlib.new('sha256')
        if data is not None:
            self.add_data(data)

    def reset(self):
        self.hasher = hashlib.new('sha256')

    def add_file(self, filename):
        with open(filename, 'rb') as fp:
            self.hasher.update(fp.read())

    def add_data(self, data):
        self.hasher.update(data)

    def digest(self):
        return self.hasher.hexdigest()

    @classmethod
    def hash_files(cls, files):
        h = cls()
        for name in files:
            h.add_file(name)
        return h.digest()
