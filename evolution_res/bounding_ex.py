
# mylist = [-5, 500, 300, 200]
def bounds(mylist = []):
	l = len(mylist)
	total = 0.0
	maxE = 100

# 	Loop through the list and make sure that all values are between 0 and 100 inclusive
	for i in range(0,l):
		mylist[i] = max(min(mylist[i], 100), 0)
		total += mylist[i]

# 	Scale all list element values to sum to a total of 100
	if (total != 0):
		for i in range(0,l):
			mylist[i] = int(mylist[i] / total * maxE)
			
# 	Edge Case: Equally distribute across all list elements		
	else:
		for i in range(0, l):
			mylist[i] = (maxE / l)

# 	print mylist 

# test cases
# bounds([3, 6, 1, 0])
# bounds([0, 0, 0, 0])
# bounds([200, 200, 200, 200])
# bounds([-1, -4, -5, -9])