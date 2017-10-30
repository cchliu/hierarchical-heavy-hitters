import math

def get_constant(p0):
    a = -1.0*2.0*(1.0-2.0*(1.0-p0)**3)**2
    b = (1.0 - math.exp(a))**2
    c = 1.0/b
    return c

