"""
    Calculate precision and recall.
    
    :params mHHH: reported list of HHHes.
    :params tHHH: true list of HHHes.

"""
def precision(mHHH, tHHH):
    if not mHHH:
        return 0
    overlap = sum([1 for k in mHHH if k in tHHH])
    p = overlap / float(len(mHHH)) * 100
    return p

def recall(mHHH, tHHH):
    overlap = sum([1 for k in mHHH if k in tHHH])
    r = overlap / float(len(tHHH)) * 100
    return r 

def error_function(mHHH, tHHH):
    if len(mHHH) != len(tHHH):
        return 1

    for k in mHHH:
        if not k in tHHH:
            return 1
    
    return 0
