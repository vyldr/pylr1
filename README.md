# Blender import add-on for Lego Racers files
This is a Blender add-on for importing Lego Racers files.  Currently supported file types include:
- `.GDB` 3D objects (not all gdb files work yet)
- `.BVB` Bounding volumes and checkpoints

## Installation
1. Download the latest release from the [releases page](https://github.com/vyldr/pylr1/releases) or build it yourself
2. Open Blender
3. Go to `Edit` -> `Preferences`
4. Click on the `Add-ons` tab
5. Click on `Install from disk`
6. Select the downloaded `.zip` file

## Usage
1. Go to `File` -> `Import` -> `Lego Racers Files`
2. Select the file to import

## Building the add-on
```bash
# Clone the repository
git clone https://github.com/vyldr/pylr1.git

# Navigate to the directory
cd pylr1

# Build the Blender add-on
blender --command extension build --source-dir $PWD/lr1 --output-dir $PWD
```
## Notes
- The add-on is still in development
- Supports Blender 4.2 and later versions.
- Tested on Linux, MacOS, and Windows.
