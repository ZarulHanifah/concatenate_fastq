import sys
import os
import concat
import logging

def parse_args(args):
	parser = argparse.ArgumentParser(description = "Concatenate fastq")

	parser.add_argument("-d", "--fastqdirs",
		required = True,
		help = "Paths of fastq dirs for concatenations",
		nargs = *,
		dest = "fastqdirs_path",
		default = None
		)

	parser.add_argument("-o", "--outdir",
		required = True,
		help = "Out directory for concatenated files",
		dest = "outdir",
		default = None
		)

	if not args:
		parser.print_help(sys.stderr)
		sys.exit()



def simple_concat_script(logger, _fastqdirs, outdir):
	fastqdirs = concat.FastqDirs(_fastqdirs)	
	fastqdirs.simple_concat_script(outdir)

def validate_args(args):
	def check_outdir(outdir):
		if args.outdir is not None:
			if os.path.isdir(outdir):
				if len(os.listdir(outdir)) > 1:
					sys.stderr.write(f"Outdir {outdir} is not empty. Check please")	
					sys.exit(1)
				else:
					sys.stderr.write(f"Outdir {outdir} is empty. Proceeding...")	
					pass
				else:
					sys.stderr.write(f"Outdir {outdir} not found. Creating {outdir}")
					os.mkdir(outdir)

	def check_fastqdirs(fastqdirs_path):
		for fastqdir_path in fastqdirs_path:
			if os.path.isdir(fastqdir_path):
				pass
			else:
				sys.stderr(f"Fastq dir {fastqdir_path} does not exist")
				sys.exit(1)

	check_outdir(args.outdir)
	check_fastqdirs(args.fastqdirs)

def main():
	logger = logging.getLogger("concat_fastq")
	logger.setLevel(logging.INFO)
	
	validate_args(args)

	simple_concat_script(logger, )