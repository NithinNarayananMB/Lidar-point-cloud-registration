
## 🛠️ How to Actually Run This (Step-by-Step)

Want to run this on your own machine? It’s super easy. Just follow these steps:

### Step 1: Prep your files
For this pipeline to work, you need two Python files sitting together in the exact same folder:
* **`main.py`** (or whatever you named the main script). This acts as the manager—it scans the folders, acts as the gatekeeper, and logs all the text files.
* **`registration.py`** This is the engine room! The main script imports this file because it holds the actual mathematical functions (`run_standard_icp`, `run_robust_icp`, etc.) that do the heavy lifting when it's time to align the point clouds.

### Step 2: Install the tools
Open your terminal or command prompt and install Open3D and NumPy so Python knows how to handle the 3D geometry:
```bash
pip install open3d numpy
Step 3: Point it to your data
Open your main script and look for the folder_path variable. Change it to point exactly to the folder holding your .ply, .pcd, or .xyz files.

Python
folder_path = r"C:\Users\YourName\Desktop\My_Point_Clouds"
Step 4: Choose your visual settings
Find the two visualization toggles at the top of the main script. Change them to True or False depending on what you want to see pop up on your screen today:

Python
VISUALIZE_REJECTED = True  # Pops open a 3D window to show you WHY a pair failed
VISUALIZE_PERFECT = False  # Silently saves the good matches in the background
Step 5: Run it!
Run the main script from your terminal. Sit back and let the code do the manual labor for you.

Bash
python main.py
Step 6: Check your results
Once the script says "BATCH PROCESSING COMPLETE", look inside your folder. You will magically have three new text files (results.txt, batch_results.txt, and rejected.txt) containing all your sorted data and metrics!