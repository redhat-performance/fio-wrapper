import pydantic
import datetime
from enum import Enum
class Benchmark(Enum):
    read = "read"
    write = "write"

class Fio_Results (pydantic.BaseModel):
    op: Benchmark
    blocksize_KiB: int = pydantic.Field(gt=0)
    njobs: int = pydantic.Field(gt=0)
    ndisks: int = pydantic.Field(gt=0)
    iodepth: int = pydantic.Field(gt=0)
    bw_KiB_s: float = pydantic.Field(gt=0, allow_inf_nan=False)
    iops: float = pydantic.Field(gt=0, allow_inf_nan=False)
    clat_us: int = pydantic.Field(ge=0)
    lat_us: int = pydantic.Field(ge=0)
    slat_us: int = pydantic.Field(ge=0)
    Start_Date: datetime.datetime
    End_Date: datetime.datetime
