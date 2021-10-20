#!/usr/bin/env python

import sys
import os
import concat
import logging
import argparse

def parse_args(args):
	parser = argparse.ArgumentParser(description = "Concatenate fastq")
	parser.add_argument("-f", "--fastqdirs",
		required = True,
		help = "Paths of fastq dirs for concatenations",
		nargs = "*",
		dest = "fastqdirs_path",
		default = None
		)

	parser.add_argument("-o", "--outdir",
		required = True,
		help = "Out directory for concatenated files",
		dest = "outdir",
		default = None
		)

	parser.add_argument("--print-only",
		required = False,
		help = "Only print, don't concat yet",
		dest = "print_only",
		action = "store_true"
		)

	if not args:
		parser.print_help(sys.stderr)
		sys.exit()
	return parser.parse_args(args)

def print_concat_script(fastqdirs_path, outdir):
	fastqdirs = concat.FastqDirs(fastqdirs_path)	
	fastqdirs.print_concat_script(outdir)

def concatenate_fastq(fastqdirs_path, outdir):
	fastqdirs = concat.FastqDirs(fastqdirs_path)	
	fastqdirs.concatenate_fastq(outdir)

def validate_args(args):
	def check_outdir(args):
		outdir = args.outdir
		if outdir is not None:
			if os.path.isdir(outdir):
				if len(os.listdir(outdir)) > 1:
					if not args.print_only:
						print(f"Outdir {outdir} is not empty. Check please")
						sys.exit(1)
				else:
					print(f"Outdir {outdir} is empty. Proceeding...")	
					pass
			else:
				print(f"Outdir {outdir} not found. Creating {outdir}")
				
	def check_fastqdirs(fastqdirs_path):
		for fastqdir_path in fastqdirs_path:
			if os.path.isdir(fastqdir_path):
				pass
			else:
				logger.info(f"Fastq dir {fastqdir_path} does not exist")
				sys.exit(1)

	check_outdir(args)
	check_fastqdirs(args.fastqdirs_path)

def main():
		
	args = sys.argv[1:]
	args = parse_args(args)
	
	validate_args(args)

	if args.print_only:
		print_concat_script(args.fastqdirs_path, args.outdir)
	else:
		if os.path.isdir(args.outdir) == False:
			os.mkdir(args.outdir)
		concatenate_fastq(args.fastqdirs_path, args.outdir)

if __name__ == "__main__":
	main()