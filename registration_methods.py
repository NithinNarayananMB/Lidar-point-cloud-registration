import open3d as o3d
import numpy as np

def run_standard_icp(source, target, threshold=0.02, trans_init=np.identity(4)):
    result = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane()
    )
    return result


def run_sparse_gicp(source, target, threshold=0.02, trans_init=np.identity(4), voxel_size=0.005):
    # 1. Downsample
    source_sparse = source.voxel_down_sample(voxel_size)
    target_sparse = target.voxel_down_sample(voxel_size)

    # 2. Re-calculate normals for the new sparse structure
    source_sparse.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    target_sparse.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    # 3. Execute GICP
    result = o3d.pipelines.registration.registration_generalized_icp(
        source_sparse, target_sparse, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationForGeneralizedICP()
    )
    return result


def run_robust_icp(source, target, threshold=0.02, trans_init=np.identity(4), huber_k=0.01):
    robust_loss = o3d.pipelines.registration.HuberLoss(k=huber_k)

    result = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(robust_loss)
    )
    return result