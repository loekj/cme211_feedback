from math import sqrt
def mean(l):
	return float(sum(l))/len(l) if len(l) > 0 else float('nan') 

def sampleStd(l):
	if len(l) == 0:
		return float('nan')
	avg = mean(l)
	return sqrt(float( sum( map(lambda x: (x - avg)**2, l) ) ) / (len(l) - 1))