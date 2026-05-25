import open3d as o3d
import os
import copy
import numpy as np
import time
from itertools import combinations

from registration_methods import run_standard_icp, run_robust_icp, run_sparse_gicp


def view_alignment(source, target, transformation=None, title="3D Viewer"):
    """Visualizes the alignment of two point clouds."""
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)

    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])

    if transformation is not None:
        source_temp.transform(transformation)

    print(f"\nOpening 3D viewer: [{title}]")
    print("Controls: Left Click to Rotate | Right Click to Pan | Scroll to Zoom")
    print("NOTE: Close the viewer window to continue the batch process.")

    o3d.visualization.draw_geometries(
        [source_temp, target_temp],
        window_name=title
    )


def methodinfo(source_path, target_path, method_name, run_time, fitness, rmse):
    """Logs detailed method metrics to the batch results file."""
    with open("batch_results.txt", "a") as file:
        file.write(f"Method:   {method_name}\n")
        file.write(f"Source:   {os.path.basename(source_path)}\n")
        file.write(f"Target:   {os.path.basename(target_path)}\n")
        file.write(f"Time:     {run_time:.4f} seconds\n")
        file.write(f"Scores:   Fitness: {fitness:.4f} | RMSE: {rmse:.4f}\n")
        file.write("-" * 60 + "\n")


def log_rejected_pair(source_path, target_path, stage, fitness, rmse="N/A"):
    """Logs rejected point cloud pairs and the reason for rejection to a separate file."""
    with open("rejected.txt", "a") as file:
        file.write(f"REJECTED [{stage}]: [{os.path.basename(source_path)}] <---> [{os.path.basename(target_path)}]\n")

        # Format the RMSE string depending on whether it's a number or "N/A"
        rmse_str = f"{rmse:.4f}" if isinstance(rmse, (int, float)) else rmse
        file.write(f"    Scores at rejection -> Fitness: {fitness:.4f} | RMSE: {rmse_str}\n")
        file.write("-" * 60 + "\n")


if __name__ == "__main__":

    # =========================================================
    # Change here
    # =========================================================
    folder_path = r"Enter the folder path"

    my_threshold = 0.02
    minimum_required_fitness = 0.30
    validation_fitness_min = 0.80
    validation_rmse_max = 0.0065

    # --- VISUALIZATION TOGGLES ---
    # ---Set True or False---
    VISUALIZE_REJECTED = True
    VISUALIZE_PERFECT = True

    valid_extensions = [".ply", ".pcd", ".xyz"]
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                 if os.path.splitext(f)[1].lower() in valid_extensions]

    if len(all_files) < 2:
        print("Error: Need at least 2 point clouds in the folder to create pairs.")
        exit()

    file_pairs = list(combinations(all_files, 2))

    print("\n" + "=" * 60)
    print(f" PIPELINE INITIALIZED")
    print(f" Found {len(all_files)} files. Testing {len(file_pairs)} possible combinations.")
    print("=" * 60)

    for source_path, target_path in file_pairs:
        print(f"\n>>> Analyzing Pair: [{os.path.basename(source_path)}] & [{os.path.basename(target_path)}]")

        source = o3d.io.read_point_cloud(source_path)
        target = o3d.io.read_point_cloud(target_path)

        if source.is_empty() or target.is_empty():
            print("    [!] Corrupt file detected. Skipping.")
            continue

        initial_transform = np.identity(4)
        initial_eval = o3d.pipelines.registration.evaluate_registration(
            source, target, my_threshold, initial_transform
        )

        # --- REJECTION STAGE 1: THE GATEKEEPER ---
        if initial_eval.fitness < minimum_required_fitness:
            print(f"    [X] Rejected: Initial overlap too low ({initial_eval.fitness:.2f}). Skipping math.")
            log_rejected_pair(source_path, target_path, "GATEKEEPER", initial_eval.fitness)

            if VISUALIZE_REJECTED:
                title_gatekeeper = f"REJECTED (Gatekeeper): {os.path.basename(source_path)} & {os.path.basename(target_path)}"
                view_alignment(source, target, initial_transform, title_gatekeeper)

            continue

        # --- IF ACCEPTED, RUN STANDARD ICP FIRST ---
        print(f"    [+] Initial Overlap is {initial_eval.fitness:.2f}. Running Standard ICP...")
        source.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        start_time_std = time.perf_counter()
        result_std = run_standard_icp(source, target)
        run_time_std = time.perf_counter() - start_time_std

        # --- REJECTION STAGE 2: THE POST-EXECUTION VALIDATOR ---
        if result_std.fitness < validation_fitness_min or result_std.inlier_rmse > validation_rmse_max:
            print(
                f"    [-] Match failed validation (Fit: {result_std.fitness:.2f}, RMSE: {result_std.inlier_rmse:.4f}). Discarding.")
            log_rejected_pair(source_path, target_path, "VALIDATOR", result_std.fitness, result_std.inlier_rmse)

            if VISUALIZE_REJECTED:
                title_validator = f"REJECTED (Validator): {os.path.basename(source_path)} & {os.path.basename(target_path)}"
                view_alignment(source, target, result_std.transformation, title_validator)

            continue

        print("    [★] PERFECT MATCH VERIFIED! Running remaining algorithms and saving data...")

        # Robust ICP
        start_time_rob = time.perf_counter()
        result_rob = run_robust_icp(source, target)
        run_time_rob = time.perf_counter() - start_time_rob

        # Sparse GICP
        start_time_spa = time.perf_counter()
        result_spa = run_sparse_gicp(source, target)
        run_time_spa = time.perf_counter() - start_time_spa

        # --- WRITE ONLY PERFECT MATCHES TO FILES ---
        methodinfo(source_path, target_path, "Standard ICP", run_time_std, result_std.fitness, result_std.inlier_rmse)
        methodinfo(source_path, target_path, "Robust ICP", run_time_rob, result_rob.fitness, result_rob.inlier_rmse)
        methodinfo(source_path, target_path, "Sparse ICP", run_time_spa, result_spa.fitness, result_spa.inlier_rmse)

        with open("results.txt", "a") as file:
            file.write(f"VERIFIED MATCH: [{os.path.basename(source_path)}] <---> [{os.path.basename(target_path)}]\n")
            file.write(f"    Initial Overlap: {initial_eval.fitness:.4f}\n")
            file.write(f"    Final Fitness:   {result_std.fitness:.4f}\n")
            file.write(f"    Final RMSE:      {result_std.inlier_rmse:.4f}\n")
            file.write("-" * 60 + "\n")

        # --- VISUALIZATION OF PERFECT MATCHES ---
        if VISUALIZE_PERFECT:
            print("    [!] Opening visualizations. Close each window to proceed to the next one.")

            title_std = f"SUCCESS (Standard ICP): {os.path.basename(source_path)} & {os.path.basename(target_path)}"
            view_alignment(source, target, result_std.transformation, title_std)

            title_rob = f"SUCCESS (Robust ICP): {os.path.basename(source_path)} & {os.path.basename(target_path)}"
            view_alignment(source, target, result_rob.transformation, title_rob)

            title_spa = f"SUCCESS (Sparse GICP): {os.path.basename(source_path)} & {os.path.basename(target_path)}"
            view_alignment(source, target, result_spa.transformation, title_spa)

    print("\n" + "=" * 60)
    print(" BATCH PROCESSING COMPLETE")
    print(" Check 'batch_results.txt' for metrics, 'results.txt' for matches, and 'rejected.txt' for failures.")
    print("=" * 60)