args = None

def compliantLog(*inputs):
	if not args.quiet:
		print(*inputs)

def verboseLog(*inputs):
	if args.verbose:
		print(*inputs)