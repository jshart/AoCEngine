class HashTracker:
    def __init__(self):
        self.count = 0
        self.hash = dict()
    
    def add(self, hash):
        # does this already exist in the dict?
        if hash in self.hash:
            self.hash[hash] += [self.count]
            self.count += 1
            return(self.hash[hash])
        else:
            self.hash[hash] = [self.count]
            self.count += 1
            return(None)
    