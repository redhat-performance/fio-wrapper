Automation wrapper for fio

Description:
                Fio spawns a number of threads or processes doing a particular type
                of I/O action as specified by the user. fio takes a number of global
                parameters, each inherited by the thread unless other parameters
                provided for that thread overrides the global settings. The typical use of
                fio is to write a job file matching the I/O load one wants to simulate.

Location of underlying workload: https://fio.readthedocs.io/en/latest/fio_doc.html
   benchmark loaded via dnf

Packages required: gcc,numactl,python3,bc,fio

To run:
```
[root@hawkeye ~]# git clone https://github.com/redhat-performance/fio-wrapper
[root@hawkeye ~]# fio-wrapper/fio/fio_run
```

Defaults for the script are the following:
```
	devices: No default, if not provided will be prompted
        run time: 120 seconds
        test type: read and write
        ioengine: libaio
        jobs min: 1
        jobs max: # numa nodes
        block size: 4k and 1024k
	io depth: 1 2 4 8 16 32
       
If regression option is selected, only one set of runs with all the disks.
	devices: No default, if not provided will be prompted
        run time: 120 seconds
        test type: read and write
        ioengine: libaio
        jobs min: 1
        jobs max: # numa nodes
        block size: 4k and 1024k
	io depth: 1 16 64
```
Options
```
Usage: fio-wrapper/fio/fio_run
  --block_size: comma separated lists of block sizes to use
  --disk_size: size in M, use this as the size of the disk instead of lsblk
  --disks: comma separated list of disks to use.
  --ioengine: comma separated list of ioengines to use
  --iodepth_list: how many ios are allowed outstanding
  --jobs_list: comma separated list of jobs, overrides jobs max and jobs_min, numa_node means use
    number of numa nodes or 2, which ever is greater
  --jobs_max: maximum number of jobs to run
  --jobs_min: minimum number of jobs to run
  --max_disks: maximum number of disks to run with
  --max_disks_only: Perform the run only with maximum disks
  --regression: regression run
  --runtime: run for the designated period, 60 seconds is the default
  --test_type: type of io doing.
General options
  --home_parent <value>: Our parent home directory.  If not set, defaults to current working directory.
  --host_config <value>: default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --run_user: user that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname.  Defaults to hostname.
  --sysname: name of the system running, used in determining config files.  Defaults to hostname.
  --tuned_setting: used in naming the tar file, default for RHEL is the current active tuned.  For non
    RHEL systems, default is none.
  --usage: this usage message.
```

