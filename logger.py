args = None

def compliantLog(*inputs):
	if not args.quiet:
		print(*inputs)

def verboseLog(*inputs):
	if args.verbose:
		print(*inputs)
		
def alreadyExist(path):
	if args.verbose:
		print('\n' + path, "already exists! Will not overwrite!")