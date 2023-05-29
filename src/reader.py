class Reader:
    def __init__(self):
        self.file = None

    def reset(self, filename):
        if self.file is not None:
            self.file.close()
        self.file = open(filename, "r")

    def read_next_line(self):
        return self.file.readline()


reader = Reader()
