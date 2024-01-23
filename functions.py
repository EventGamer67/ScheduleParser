import hashlib

def areSameFiles(filePath1, filePath2):
    with open(filePath1, 'rb') as file1, open(filePath2, 'rb') as file2:
        content1 = file1.read()
        content2 = file2.read()
        return compare_hashes(content1, content2)
def compare_hashes(data1, data2):
    hash1 = hashlib.sha256(data1).hexdigest()
    hash2 = hashlib.sha256(data2).hexdigest()

    if hash1 == hash2:
        return True
    else:
        return False

def getFileHash(filePath):
    with open(filePath, 'rb') as file1:
        return hashlib.sha256(file1.read()).hexdigest()
