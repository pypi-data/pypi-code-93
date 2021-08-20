import json
from typing import Optional, Tuple, cast
from cloudvolume.exceptions import OutOfBoundsError

import numpy as np
from time import time

import tinybrain
from cloudfiles import CloudFiles
from taskqueue.registered_task import RegisteredTask

from cloudvolume import Bbox, CloudVolume, Vec
from cloudvolume.datasource.precomputed.sharding import ShardingSpecification
from cloudvolume.frontends.precomputed import CloudVolumePrecomputed

# from ilock import ILock


class ShardTask(RegisteredTask):
    def __init__(
        self,
        src_path: str,
        dst_path: str,
        dst_bbox: Bbox,
        *,
        mip: int = 0,
        num_mips: int = 0,
        fill_missing: bool = False,
        background_color: int = 0,
        translate: Tuple[int, int, int] = (0, 0, 0),
        skip_first_mip: bool = False,
        sparse: bool = False,
    ):
        super().__init__(src_path, dst_path, dst_bbox, mip=mip, num_mips=num_mips, fill_missing=fill_missing, background_color=background_color, translate=translate, skip_first_mip=skip_first_mip, sparse=sparse)
        self.src_path = src_path
        self.dst_path = dst_path
        self.dst_bbox = dst_bbox
        self.mip = mip
        self.num_mips = num_mips
        self.fill_missing = fill_missing
        self.background_color = background_color
        self.translate = Vec(*translate)
        self.skip_first_mip = skip_first_mip
        self.sparse = sparse

    @staticmethod
    def calc_minishard_size(
        vol: CloudVolumePrecomputed,
        *,
        mip: Optional[int] = None,
        spec: Optional[ShardingSpecification] = None,
    ) -> Vec:
        mip = vol.mip if mip is None else mip
        scale = vol.meta.scale(mip)

        try:
            spec = spec or ShardingSpecification.from_dict(scale["sharding"])
        except KeyError:
            raise ValueError(
                f"MIP {mip} does not have a sharding specification and none was supplied."
            )

        # chunks_per_minishard = [
        #     2 ** ((int(spec.preshift_bits) + 2 - i) // 3) for i in range(3)
        # ]
        chunks_per_minishard = [
            2 ** ((int(spec.preshift_bits) + i) // 3) for i in range(3)
        ]
        return vol.meta.chunk_size(mip) * chunks_per_minishard

    @staticmethod
    def calc_shard_size(
        vol: CloudVolumePrecomputed,
        *,
        mip: Optional[int] = None,
        spec: Optional[ShardingSpecification] = None,
    ) -> Vec:
        mip = vol.mip if mip is None else mip
        scale = vol.meta.scale(mip)

        try:
            spec = spec or ShardingSpecification.from_dict(scale["sharding"])
        except KeyError:
            raise ValueError(
                f"MIP {mip} does not have a sharding specification and none was supplied."
            )

        # minishards_per_shard = [
        #     2 ** ((int(spec.minishard_bits) + 2 - i) // 3) for i in range(3)
        # ]
        minishards_per_shard = [
            2 ** ((int(spec.minishard_bits) + i) // 3) for i in range(3)
        ]
        return ShardTask.calc_minishard_size(vol, mip=mip, spec=spec) * minishards_per_shard
    
    @staticmethod
    def calc_downsample_factor(
        vol: CloudVolumePrecomputed, mip_start: int, mip_stop: int
    ) -> Vec:
        factors = [(
            vol.meta.downsample_ratio(m + 1) / vol.meta.downsample_ratio(m)
        ).astype(int) for m in range(mip_start, mip_stop)]

        if len(np.unique(factors, axis=0)) > 1:
            raise ValueError(f"All MIPs must use the same downsample factor. Got {factors}")

        return factors[0]

    def execute(self):
        src_vol = CloudVolume(
            self.src_path, fill_missing=self.fill_missing, mip=self.mip, bounded=False
        )
        dst_vol = cast(
            CloudVolumePrecomputed,
            CloudVolume(
                self.dst_path,
                fill_missing=self.fill_missing,
                mip=self.mip,
                background_color=self.background_color,
                compress=None
            ),
        )

        dst_bbox = Bbox.from_dict(json.loads(self.dst_bbox))
        dst_bbox = Bbox.clamp(dst_bbox, dst_vol.meta.bounds(self.mip))
        dst_bbox = dst_bbox.expand_to_chunk_size(
            dst_vol.meta.chunk_size(self.mip), offset=dst_vol.meta.voxel_offset(self.mip)
        )

        src_bbox = dst_bbox - self.translate
        print(src_bbox)

        # with ILock("shard-task-download"):
        s = time()
        ds_results = [src_vol.download(src_bbox)]

        ds_factor = Vec(1,1,1)
        print(f"Download {src_bbox.size3()} finished in {round(time() - s, 2)} s")

        if self.num_mips > 0:
            s = time()
            ds_factor = ShardTask.calc_downsample_factor(dst_vol, self.mip, self.mip + self.num_mips)
            ds_results.extend([np.empty_like(ds_results[0], shape=tuple(max(1, d // (f**(i+1))) for d, f in zip(ds_results[0].shape, [*ds_factor, 1]))) for i in range(self.num_mips)])

            if dst_vol.layer_type == "image":
                fn, kwargs = tinybrain.downsample_with_averaging, {"sparse": ds_factor[-1] > 1}
            elif dst_vol.layer_type == "segmentation":
                fn, kwargs = tinybrain.downsample_segmentation, {"sparse": self.sparse}
            else:
                fn, kwargs = tinybrain.downsample_with_striding, {}

            ds_part_size = 512
            ds_grid = list(range(0, ds_results[0].shape[j], ds_part_size) for j in range(3))
            for ds_offset in np.array(np.meshgrid(*ds_grid)).T.reshape(-1, 3):
                x,y,z = ds_offset
                ds_parts = fn(ds_results[0][x:x+ds_part_size,y:y+ds_part_size,z:z+ds_part_size], ds_factor, num_mips=self.num_mips, **kwargs)
                for i in range(self.num_mips):
                    sx2, sy2, sz2 = ds_parts[i].shape[:3]
                    x2, y2, z2 = [d // f**(i+1) for d, f in zip(ds_offset, ds_factor)]
                    ds_results[i+1][x2:x2+sx2, y2:y2+sy2, z2:z2+sz2] = ds_parts[i]

            # ds_results.extend(fn(ds_results[0], ds_factor, num_mips=self.num_mips, **kwargs))
            if self.skip_first_mip:
                ds_results[0] = None
            print(f"Downsampling from {self.mip} to {self.mip + self.num_mips} finished in {round(time() - s, 2)} s")

        # Create make_shard tasks - assumes shards from all MIP align with
        # original task bounds

        mip_start = self.mip
        task_size = dst_bbox.size3()
        task_offset = dst_bbox.minpt

        for i, img in enumerate(ds_results):
            mip_curr = mip_start + i

            if self.skip_first_mip and mip_curr == mip_start:
                continue

            
            task_offset_mip_curr = task_offset // ds_factor ** (mip_curr - mip_start)
            task_size_mip_curr = task_size // ds_factor ** (mip_curr - mip_start)

            shard_size = ShardTask.calc_shard_size(dst_vol, mip=mip_curr)
            shard_grid = (range(0, task_size_mip_curr[j], shard_size[j]) for j in range(3))

            for rel_shard_offset in np.array(np.meshgrid(*shard_grid)).T.reshape(-1, 3):
                rel_shard_bbox = Bbox(rel_shard_offset, rel_shard_offset + shard_size)
                abs_shard_offset = (task_offset_mip_curr + rel_shard_offset).astype(int)
                abs_shard_bbox = Bbox(abs_shard_offset, abs_shard_offset + shard_size)

                abs_shard_bbox_clamped = Bbox.clamp(abs_shard_bbox, dst_vol.meta.bounds(mip_curr))
                if abs_shard_bbox_clamped.subvoxel():
                    print(f"Shard completely outside dataset: Requested: {abs_shard_bbox}, Dataset: {dst_vol.meta.bounds(mip_curr)}")
                    continue

                basepath = dst_vol.meta.join(
                    dst_vol.meta.cloudpath, dst_vol.meta.key(mip_curr)
                )

                print(f"Starting {abs_shard_bbox} @ MIP {mip_curr}")
                s = time()
                try:
                    (filename, shard) = dst_vol.image.make_shard(
                        img[rel_shard_bbox.to_slices()], abs_shard_bbox, mip_curr, progress=True
                    )
                except OutOfBoundsError:
                    print("STILL FAILING")
                    continue

                print(f"Make shard {filename} finished in {round(time() - s, 2)} s")

                # with ILock("shard-task-download"):
                s = time()
                CloudFiles(basepath).put(filename, shard)
                print(f"Upload shard {filename} finished in {round(time() - s, 2)} s")