# FIO (Flexible I/O Tester) Benchmark Wrapper

## Description

This wrapper facilitates the automated execution of the [FIO](https://fio.readthedocs.io/en/latest/fio_doc.html) (Flexible I/O Tester) benchmark. FIO spawns a number of threads or processes performing a particular type of I/O action as specified by the user, measuring throughput (bandwidth in KiB/s), IOPS, and latency (completion, submission, and total latency in microseconds).

The wrapper provides:
- Automated FIO installation, configuration, and execution.
- Disk sweep across increasing disk counts (1, 2, 4, 8, ... N).
- Configurable test matrix: block sizes, I/O depths, job counts, I/O engines, and operation types.
- Support for raw block devices, filesystem-backed files, and LVM volumes.
- Automatic NUMA-aware job count calculation.
- Regression mode for quick validation runs.
- Result collection, CSV aggregation, and JSON validation.
- System configuration metadata capture.
- Integration with test_tools framework.
- Optional Performance Co-Pilot (PCP) integration.

## Command-Line Options

```
FIO Wrapper Options:
  --block_size <value>: Comma separated list of block sizes in KiB to use.
      Default: 4,1024
  --disk_size <value>: Size in bytes. Use this as the size of the disk instead of
      querying lsblk.
  --disks <value>: Comma separated list of disk devices to use (e.g. /dev/sdb,/dev/sdc).
      If not provided, the wrapper will prompt for device selection.
  --file_count <value>: Number of files to create per disk mount point.
      When set to a value greater than 0, creates filesystems and uses files
      instead of raw devices. Default: 0 (use raw devices).
  --file_size <value>: Size of each file in GiB when using filesystem-backed files.
      Default: 10
  --fs_type <value>: Filesystem type to create when using --file_count.
      Default: xfs
  --ioengine <value>: Comma separated list of I/O engines to use.
      Default: libaio
  --iodepth_list <value>: Comma separated list of I/O depths (outstanding I/Os).
      Default: 1,2,4,8,16,32 (regression: 1,16,64)
  --jobs_list <value>: Comma separated list of job counts. Overrides --jobs_max and
      --jobs_min. The keyword "numa_node" is replaced with the number of NUMA nodes
      (minimum 2).
  --jobs_max <value>: Maximum number of jobs to run. Default: number of NUMA nodes.
  --jobs_min <value>: Minimum number of jobs to run. Default: 1
  --lvm: Use LVM. Combines all specified disks into a single LVM logical volume.
  --max_disks <value>: Maximum number of disks to include in the sweep.
  --max_disks_only: Skip the disk sweep and perform the run only with the maximum
      number of disks.
  --regression: Run in regression mode (reduced I/O depth list, single + all disk runs).
  --runtime <value>: Duration of each FIO run in seconds. Default: 120
  --test_type <value>: Comma separated list of I/O operation types to test.
      Default: read,write
      Supported: read, write, trim, randread, randwrite, randtrim, rw, readwrite,
      randrw, trimwrite, randtrimwrite

General test_tools options:
  --home_parent <value>: Parent home directory. If not set, defaults to current
      working directory.
  --host_config <value>: Host configuration name, defaults to current hostname.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --run_user: User that is actually running the test on the test system.
      Defaults to current user.
  --sys_type: Type of system working with (aws, azure, hostname).
      Defaults to hostname.
  --sysname: Name of the system running, used in determining config files.
      Defaults to hostname.
  --tuned_setting: Used in naming the results directory. For RHEL, defaults to
      current active tuned profile. For non-RHEL systems, defaults to 'none'.
  --use_pcp: Enable Performance Co-Pilot monitoring during test execution.
  --tools_git <value>: Git repo to retrieve the required tools from.
      Default: https://github.com/redhat-performance/test_tools-wrappers
  --usage: Display the usage message.
```

## What the Script Does

The `fio_run` script performs the following workflow:

1. **Environment Setup**:
   - Clones the test_tools-wrappers repository if not present (default: `~/test_tools`).
   - Sources error codes and general setup utilities.
   - Prompts for disk devices if `--disks` was not provided.

2. **Package Installation**:
   - Installs required dependencies via `package_tool` using the package manifest (`fio-wrapper.json`).
   - Dependencies are defined per OS variant (RHEL, Ubuntu, Amazon Linux).

3. **Device Validation**:
   - Verifies each specified device is a block device.
   - Checks that no specified device is currently mounted.
   - When using `--file_count`, creates and mounts filesystems instead.

4. **FIO Installation**:
   - Locates the `fio` binary in `/usr/local/bin`, `/bin`, or `/usr/bin`.
   - Copies it to `/usr/local/bin` if not already present there.

5. **Test Matrix Construction**:
   - Builds the sweep matrix from block sizes, I/O depths, job counts, I/O engines, and operation types.
   - Determines disk size via `lsblk` (or `--disk_size` override).
   - Calculates job counts by doubling from `jobs_min` to `jobs_max`.

6. **Test Execution**:
   - Generates FIO job files with direct I/O, time-based runs, and a 5-second ramp time.
   - In sweep mode: tests with 1 disk, 2 disks, then 4, 8, 16, ... up to `max_disks`.
   - In regression mode: tests with 1 disk, then all disks.
   - Records start and end timestamps for each run.
   - Optionally logs test knobs and results to PCP.

7. **Result Processing**:
   - Extracts bandwidth (bw_mean), IOPS, completion latency (clat), submission latency (slat), and total latency (lat) from FIO JSON output.
   - Converts latencies from nanoseconds to microseconds.
   - Generates sorted CSV files per metric per operation type.
   - Merges per-metric CSVs into a unified `results_fio.csv`.

8. **Validation**:
   - Converts CSV to JSON via `csv_to_json` from test_tools.
   - Validates results against the Pydantic schema (`results_fio_schema.py`).

9. **Output**:
   - Creates a timestamped results directory: `export_fio_data_YYYY.MM.DD-HH.MM.SS`.
   - Creates an `export_fio_data` symlink pointing to the latest results.
   - Saves all raw FIO JSON output, processed CSVs, system metadata, and logs.
   - Optionally saves PCP performance data.
   - Archives results to a configured storage location via `save_results`.

10. **Cleanup**:
    - Unmounts filesystems and removes LVM volumes if `--file_count` or `--lvm` was used.

## Dependencies

Location of underlying workload: installed via system package manager (`dnf`/`apt`). Documentation: https://fio.readthedocs.io/en/latest/fio_doc.html

**RHEL packages**: bc, fio, gcc, git, make, perf, python3, unzip, zip

**Ubuntu packages**: bc, fio, gcc, git, make, linux-tools-generic, python3, unzip, zip

**Amazon Linux packages**: bc, fio, git, unzip, zip

To run:
```bash
git clone https://github.com/redhat-performance/fio-wrapper
cd fio-wrapper/fio
./fio_run --disks /dev/sdb
```

The script will automatically install required packages and configure the test environment.

## The FIO Benchmark

FIO (Flexible I/O Tester) is a versatile I/O workload generator used for benchmarking and stress-testing storage subsystems. It can simulate a wide variety of I/O patterns and measure performance characteristics.

### Key FIO Parameters

1. **Block Size (bs)**: The size of each I/O operation. This wrapper specifies block sizes in KiB via `--block_size` (internally multiplied by 1024 to produce byte values for FIO). Default: 4 KiB and 1024 KiB.

2. **I/O Depth (iodepth)**: The number of I/O operations to keep in flight at once. Higher values increase parallelism and can improve throughput on capable devices. Default: 1, 2, 4, 8, 16, 32.

3. **Number of Jobs (numjobs)**: The number of independent FIO threads per target device. The wrapper defaults to sweeping from 1 up to the number of NUMA nodes (doubling each step).

4. **I/O Engine (ioengine)**: The mechanism used to submit I/O. Default: `libaio` (Linux native asynchronous I/O). Other options include `io_uring`, `sync`, `psync`, etc.

5. **Performance Metrics**: FIO reports:
   - **Bandwidth** (bw) in KiB/s — sustained throughput.
   - **IOPS** — I/O operations per second.
   - **Completion Latency** (clat) — time from submission to completion.
   - **Submission Latency** (slat) — time to submit the I/O.
   - **Total Latency** (lat) — end-to-end latency (slat + clat).

## Output Files

The results directory contains:

- **results_fio.csv**: Aggregated CSV with header metadata (system info, tuned profile, test name) followed by per-run data columns: `op`, `blocksize_KiB`, `njobs`, `ndisks`, `iodepth`, `bw_KiB_s`, `iops`, `clat_us`, `lat_us`, `slat_us`, `Start_Date`, `End_Date`. Results are sorted by I/O depth within each operation/block-size group.
- **results_fio.json**: Validated JSON results (converted from CSV via `csv_to_json`, validated against `results_fio_schema.py`).
- **fio_ndisks_\<N\>\_...\/*.json**: Raw FIO JSON output files per run, organized in timestamped subdirectories with `start_time` and `end_time` markers.
- **\*.log**: FIO bandwidth, IOPS, latency, and histogram log files (per run).
- **file_run\_\<N\>**: Generated FIO job files used for each run.
- **meta_data.yml**: System metadata (CPU info, memory, NUMA topology, kernel version).
- **fio.out**: Script console output.
- **test_results_report**: Pass/fail status.
- **pcp/**: Performance Co-Pilot monitoring data (if `--use_pcp` was used).

Results are stored in a timestamped directory: `export_fio_data_YYYY.MM.DD-HH.MM.SS`. A symlink `export_fio_data` always points to the most recent results directory.

## Examples

### Basic run with a single disk
```bash
./fio_run --disks /dev/sdb
```
This runs with:
- Block sizes: 4 KiB and 1024 KiB
- I/O depths: 1, 2, 4, 8, 16, 32
- Jobs: 1 up to the number of NUMA nodes (doubling)
- Operations: sequential read and sequential write
- I/O engine: libaio
- Runtime: 120 seconds per run
- Direct I/O enabled

### Run with multiple disks
```bash
./fio_run --disks /dev/sdb,/dev/sdc,/dev/sdd,/dev/sde
```
Performs a disk sweep: 1 disk, 2 disks, 4 disks.

### Custom block sizes and I/O depths
```bash
./fio_run --disks /dev/sdb --block_size 4,8,64,512,1024 --iodepth_list 1,8,32,128
```

### Random read/write workload
```bash
./fio_run --disks /dev/sdb --test_type randread,randwrite
```

### Run with specific job counts
```bash
./fio_run --disks /dev/sdb --jobs_list 1,4,8,16
```

### Use NUMA node count as a job count
```bash
./fio_run --disks /dev/sdb --jobs_list numa_node,8,16
```
On a 4-NUMA-node system, `numa_node` resolves to `4`, producing the list `4,8,16`.

### Regression test
```bash
./fio_run --disks /dev/sdb,/dev/sdc --regression
```
Runs a reduced test matrix with I/O depths 1, 16, 64 using only 1 disk and then all disks.

### Filesystem-backed files
```bash
./fio_run --disks /dev/sdb,/dev/sdc --file_count 4 --file_size 20 --fs_type ext4
```
Creates ext4 filesystems on each disk, then creates 4 files of 20 GiB each per mount point as FIO targets.

### LVM mode
```bash
./fio_run --disks /dev/sdb,/dev/sdc --lvm --file_count 2
```
Combines all disks into a single LVM logical volume, creates one filesystem, and uses file-based targets.

### Run only with maximum disks
```bash
./fio_run --disks /dev/sdb,/dev/sdc,/dev/sdd,/dev/sde --max_disks_only
```
Skips the 1-disk, 2-disk steps and runs only with all 4 disks.

### Multiple I/O engines
```bash
./fio_run --disks /dev/sdb --ioengine libaio,io_uring
```

### Run with PCP monitoring
```bash
./fio_run --disks /dev/sdb --use_pcp
```
Collects Performance Co-Pilot data (CPU, memory, disk I/O metrics) during the run.

### Combination example
```bash
./fio_run --disks /dev/sdb,/dev/sdc --block_size 4,128,1024 \
  --iodepth_list 1,8,32 --test_type read,write,randread,randwrite \
  --jobs_list 1,4,8 --runtime 60 --use_pcp
```

## How Disk Selection Works

### Device Modes

The wrapper supports three device modes:

1. **Raw block devices** (default): Devices passed via `--disks` are used directly. FIO operates on the raw block device with direct I/O.

2. **Filesystem-backed files** (`--file_count > 0`): The wrapper creates a filesystem (`--fs_type`, default xfs) on each disk, mounts it under `/fio0`, `/fio1`, etc., and creates the specified number of files per mount point as FIO targets.

3. **LVM** (`--lvm`): All specified disks are combined into a single LVM volume group and logical volume named `fio`. A single filesystem is created and mounted at `/perf1`.

### Disk Sweep

In sweep mode (non-regression), the wrapper progressively increases the number of disks under test:
- **1 disk** → run tests
- **2 disks** → run tests
- **4 disks** → run tests
- **8 disks** → run tests
- ... (doubling each time)
- **max_disks** → run tests (always included as the final step)

Use `--max_disks_only` to skip intermediate steps and test only with all disks.

## How Job and Parameter Sizing Works

### Job Calculation

If `--jobs_list` is provided, those exact values are used. Otherwise:

1. Start at `jobs_min` (default: 1).
2. Double until reaching `jobs_max` (default: number of NUMA nodes).
3. Always include `jobs_max` as the final value.

Example on a 4-NUMA-node system with defaults: jobs 1, 2, 4.

The special keyword `numa_node` in `--jobs_list` is replaced with the actual NUMA node count (minimum 2).

### NUMA Awareness

NUMA topology is used to determine the default maximum job count:

- `jobs_max` defaults to the number of NUMA nodes reported by `lscpu`.
- If `lscpu` reports 0 NUMA nodes (e.g., in a VM), `jobs_max` defaults to 1.
- The `numa_node` keyword in `--jobs_list` resolves to the NUMA node count (minimum 2).

### I/O Engine Selection

The default I/O engine is `libaio` (Linux native asynchronous I/O). Multiple engines can be tested in a single run by passing a comma-separated list to `--ioengine`. Each engine produces a separate set of results directories.

### Runtime Control

Each individual FIO run executes for `--runtime` seconds (default: 120). FIO is configured with `time_based=1`, meaning it runs for the full duration regardless of how quickly the data set would otherwise be exhausted.

A 5-second ramp time (`ramp_time=5`) is applied before measurement begins. FIO logs bandwidth, IOPS, and latency at 1-second intervals during the run. Histogram logs are recorded at 10-second intervals (except on Amazon Linux 2).

### Regression Mode

When `--regression` is used:

- **I/O depth list** is reduced to `1, 16, 64` (instead of the full `1, 2, 4, 8, 16, 32`).
- **Disk sweep** is simplified to two runs: first disk only, then all disks.
- All other parameters (block sizes, jobs, test types) remain unchanged.

This mode is intended for quick validation and CI pipelines where full sweep coverage is not required.

### FIO Job File Configuration

Each FIO run generates a job file (`/tmp/fio_run`) with the following global settings:

| Setting | Value |
|---|---|
| `direct` | `1` (bypass OS page cache) |
| `time_based` | `1` (run for full duration) |
| `clocksource` | `gettimeofday` |
| `ramp_time` | `5` seconds |
| `sync` | `0` |
| `write_bw_log` | `fio` |
| `write_iops_log` | `fio` |
| `write_lat_log` | `fio` |
| `log_avg_msec` | `1000` (except Amazon Linux 2) |
| `write_hist_log` | `fio` (except Amazon Linux 2) |
| `log_hist_msec` | `10000` (except Amazon Linux 2) |

Per-job sections are created for each disk or file target, each with the specified `rw`, `size`, and `numjobs`.

### Test Matrix Size

The total number of individual FIO runs is the product of:
```
|block_sizes| x |iodepths| x |jobs| x |io_engines| x |test_types| x |disk_counts|
```
With defaults on a 2-NUMA-node system with 4 disks (non-regression): `2 x 6 x 2 x 1 x 2 x 3 = 144 runs`, each running for 120 seconds. Plan wall-clock time accordingly.

## How PCP Integration Works

When `--use_pcp` is enabled:

- PCP logging starts before the first test and stops after the last test.
- Test configuration knobs (ndisks, njobs, iodepth, block size, operation type) are recorded in the PCP archive before each run.
- Run results (bw, iops, clat, slat, lat) are recorded after each run.
- Metrics are reset between runs to prevent pollution.
- The PCP pmlogger configuration (`fio_pmlogger.cfg`) captures kernel CPU utilization, memory statistics, disk I/O counters, and filesystem metadata.
- PCP data is stored in the `pcp/` subdirectory of the results directory.

## Return Codes

The script uses standardized error codes from test_tools error_codes:

| Code | Meaning |
|---|---|
| `0` | Success |
| `101` | Git clone failure (test_tools) |
| `E_GENERAL` | General failure (package installation, device validation, filesystem creation, FIO execution, result validation) |

Exit codes are sourced from the test_tools `error_codes` module.

## Notes

### Supported Operating Systems
- **RHEL** (8, 9, 10+): Full support with all dependencies available via standard repositories.
- **Ubuntu**: Full support with `linux-tools-generic` for perf.
- **Amazon Linux**: Supported with a reduced package set (no gcc, make, perf, or python3 in the dependency list).

### Architecture Support
- The wrapper is architecture-agnostic. FIO and its dependencies are available on x86_64, aarch64, and other architectures supported by the OS package manager.

### Direct I/O
- All FIO runs use `direct=1`, bypassing the OS page cache. This provides accurate storage device performance measurements but requires devices or files on filesystems that support direct I/O.

### Performance Tips
- Run on an idle system for consistent results.
- Disable CPU frequency scaling (use the performance governor) for reproducible results.
- Consider the active tuned profile on RHEL systems.
- Use `--regression` for quick smoke tests; use the full sweep for comprehensive benchmarking.
- Monitor system resources with `--use_pcp` to identify bottlenecks.

### Troubleshooting
- **"Enter comma separated list of devices to use"**: The `--disks` option was not provided. Pass the devices on the command line to avoid the interactive prompt.
- **"fio does not exist in /bin either, aborting."**: FIO is not installed. Ensure the `fio` package is available in your system repositories and that `package_tool` can install it.
- **"Error: \<device\> is not a block device"**: A specified device path does not point to a block device. Verify the device path and check that symlinks resolve correctly.
- **"Error: \<device\> is mounted."**: A specified disk is currently mounted. Unmount it before running the wrapper.
- **"package_tool reported failure installing dependencies."**: Package installation failed. Check network access to package repositories and ensure you have root privileges.
- **"Error: csv_to_json failed"** or **"Error: fio data verification failed"**: Result post-processing or schema validation failed. Check that FIO produced valid JSON output and that `results_fio.json` lines are above the minimum threshold (2 lines).
- **FIO run produces empty or minimal JSON**: Check that the target device has sufficient capacity and that the runtime is long enough for the I/O engine to produce output.
- **Histogram/log options fail on Amazon Linux 2**: The wrapper automatically disables `log_avg_msec`, `write_hist_log`, and `log_hist_msec` on Amazon Linux 2 due to FIO version limitations.
