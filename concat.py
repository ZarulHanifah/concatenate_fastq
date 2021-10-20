#!/usr/bin/env python

import sys
import os
import re
from collections import defaultdict

class FastqDirs():
    def __init__(self, fqdirs):
        self.fqdirs = [FastqDir(fqdir) for fqdir in fqdirs]
        self.client_overlap = self.get_client_overlap()
        self.sample_overlap = self.get_sample_overlap()
        self.fastq_overlap = self.get_fastq_overlap()
    
    def __getitem__(self, fqdir_path: str):
        _paths = [fqdir.path for fqdir in self.fqdirs]
        idx = _paths.index(fqdir_path)
        return self.fqdirs[idx]
    
    def simple_concat_script(self, outdir: str):
        client_sample_fastqlist_dict = self.fastq_overlap
        for client in client_sample_fastqlist_dict.keys():
            print(f"#### {client}")
            count = 0
            for sample in client_sample_fastqlist_dict[client]:
                if len(client_sample_fastqlist_dict[client][sample]) > 0:
                    print(f"## {sample}")

                    r1s = client_sample_fastqlist_dict[client][sample]["R1"]
                    r1s = " ".join(r1s)
                    print(f"cat {r1s} > outdir/{sample}_S{count}_L001_R1_001.fastq.gz")

                    r2s = client_sample_fastqlist_dict[client][sample]["R2"]
                    r2s = " ".join(r2s)
                    print(f"cat {r2s} > outdir/{sample}_S{count}_L001_R2_001.fastq.gz")
                    count += 1
                else:
                    print(f"# Sample {sample} has no overlapping fastqs")
                
    def get_fastq_overlap(self):
        """Client-sample-fastq_list. Eg:
        {"client":
            {"sample1":
                {"R1": ["dir1/sample1_R1.fastq.gz", "dir2/sample1_R1.fastq.gz"],
                "R2": ["dir1/sample1_R2.fastq.gz", "dir2/sample1_R2.fastq.gz"],
            }
        }
        """
        client_sample_fastqlist_dict = {}
        for client in self.sample_overlap.keys():
            client_sample_fastqlist_dict[client] = {}
            for sample in self.sample_overlap[client].keys():
                client_sample_fastqlist_dict[client][sample] = {}
                sample_r1s = []
                sample_r2s = []
                fastqdirs_path = self.sample_overlap[client][sample]
                if len(fastqdirs_path) > 1:
                    sample_fastq_dict = {"R1": [], "R2": []}
                    for fastqdir_path in fastqdirs_path:
                        fastqdir = self[fastqdir_path]
                        sample_r1s.append(fastqdir.get_R1_path(sample))
                        sample_r2s.append(fastqdir.get_R2_path(sample))
                    client_sample_fastqlist_dict[client][sample]["R1"] = sample_r1s
                    client_sample_fastqlist_dict[client][sample]["R2"] = sample_r2s
                else:
                    pass
        return client_sample_fastqlist_dict
    
    def get_sample_overlap(self):
        """Client-sample-fastqdir. Eg:
        {"client":
            {"sample1":
                ["fastqdir1", "fastqdir2"]}
        }
        """
        client_dict = {}
        for client, fastqdirs_path in self.client_overlap.items():
            sample_dict = defaultdict(list)
            for fastqdir_path in fastqdirs_path:
                fastqdir = self[fastqdir_path]
                samples = fastqdir.get_client_samples(client)
                for sample in samples:
                    sample_dict[sample] += [fastqdir.path]
            sample_dict = dict(sample_dict)
            client_dict[client] = sample_dict
        return client_dict
            
    def get_client_overlap(self):
        my_counter = defaultdict(list)
        for fqdir in self.fqdirs:
            for client in fqdir.get_client_list():
                my_counter[client] += [fqdir.path]
        return dict(my_counter)
        
class FastqDir():
    def __init__(self, path):
        if os.path.isdir(path):
            self.path = path
        else:
            sys.exit(f"Path {path} not found")

        self.fastqs = self.get_fastqs()
        self.client_list = self.get_client_list()
    
    def __str__(self):
        return self.path
    
    def get_client_samples(self, client):
        """Get clients samples given client ID
        """
        fastqs = self.fastqs
        return list(set([re.sub("_.*", "", fastq) for fastq in fastqs if bool(re.search(f"{client}-", fastq))]))
    
    def describe(self):
        """Simple description of the dir content. Example:
        Client: JL
        Samples:
            JL-C623
            JL-NC387
        """
        for client in self.client_list:
            print(f"Client: {client}")
            client_samples = self.get_client_samples(client)
            print("Samples:")
            for client_sample in client_samples:
                print(f"\t{client_sample}")
            print()
    
    def get_R1_path(self, sample):
        """Return full R1 path of the sample
        """
        return os.path.join(self.path, self.get_R1(sample))

    def get_R2_path(self, sample):
        """Return full R2 path of the sample
        """
        return os.path.join(self.path, self.get_R2(sample))

    def get_sample__pattern__(self, sample, pattern):
        fastqs = self.fastqs
        _ = [fastq for fastq in fastqs if bool(re.search(sample, fastq))]
        return [fastq for fastq in _ if pattern in fastq][0]
    
    def get_R1(self, sample):
        return self.get_sample__pattern__(sample, "_R1_")

    def get_R2(self, sample):
        return self.get_sample__pattern__(sample, "_R2_")
    
    def get_client_list(self):
        """ Getting client list in fastq dir
        """
        fastqs = self.fastqs
        client_list = list(set([re.sub("-.*", "", file) for file in fastqs]))
        return client_list
        
    def get_fastqs(self):
        """ Get all fastqs in dir
        A fastq file name must have:
            - "gz" (compressed)
            - "-" (First dash separates client and sample name)
        """
        _ = [file for file in os.listdir(self.path) if bool(re.search("gz", file))]
        return [file for file in _ if bool(re.search("-", file))]
    