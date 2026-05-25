

## 🛠️ How to Run This (The Easy Way)

Want to test this out on your own computer? Just follow these quick steps:

### Step 1: Get your file ready
You just need the single Python script (`main_test.py`) saved on your computer.

### Step 2: Download the required tools
Open your terminal (or command prompt) and tell Python to install Open3D and NumPy so it understands 3D shapes:

pip install open3d numpy

Step 3: Tell the code where your 3D models live
Open main_test.py and find the folder_path variable near the top. Just paste the folder path where you keep your .ply or .pcd files.

folder_path = r"upload your folderpath here"


Step 4: Pick what you want to see
There are two switches in the code. Change them to True or False depending on what you feel like looking at:

Python
VISUALIZE_REJECTED = True  # Pops open a 3D window to show you exactly WHY a pair failed
VISUALIZE_PERFECT = False  # Set to False to let it silently save the good matches in the background

Step 5: Let it run!
Open your terminal, run the script, and sit back:

python main_test.py

⚠️ IMPORTANT NOTICE ABOUT THE 3D VIEWER: > If you have the visualization switches set to True, the script will pause execution every time a 3D window pops up. It cannot move on to the next pair of point clouds until you review the current one. You must manually close the 3D viewer window to let the script continue running.


Step 6: Check your newly organized data
Once the terminal says "BATCH PROCESSING COMPLETE", check your folder. You’ll magically see three new text files with all your perfectly sorted data:

results.txt (A quick list of the perfect matches)

batch_results.txt (The nerdy math and timing stats for the matches)

rejected.txt (A list of exactly what failed and why)
