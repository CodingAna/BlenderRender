import bpy

print("device -----------------------------------------------------------------")
print(bpy.context.scene.cycles.device)
bpy.context.scene.cycles.device = "GPU"
print(bpy.context.scene.cycles.device)
bpy.ops.render.render(True)
"""
with open("hallo.txt", "w") as f:
    f.write("HALLO")

scene = bpy.context.scene
scene.cycles.device = "GPU"

prefs = bpy.context.preferences
cprefs = prefs.addons["cycles"].preferences

for compute_device_type in ("CUDA", "OPENCL", "NONE"):
    print(compute_device_type)
    try:
        cprefs.compute_device_type = compute_device_type
        print("set " + compute_device_type)
        break
    except TypeError:
        pass

print("cprefs")
print(cprefs)
print("devices")
for device in cprefs.devices:
    print("device=" + str(device))
    device.use = True
print("end-devices")
"""
