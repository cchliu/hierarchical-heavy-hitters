"""
    Calculate precision and recall.
    
    :params rHHH: reported list of HHHes.
    :params tHHH: true list of HHHes.

"""
def precision(rHHH, tHHH):
    overlap = sum([1 for k in rHHH if k in tHHH])
    p = overlap / float(len(rHHH)) * 100
    return p

def recall(rHHH, tHHH):
    overlap = sum([1 for k in rHHH if k in tHHH])
    r = overlap / float(len(tHHH)) * 100
    return r 
