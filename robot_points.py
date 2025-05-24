import numpy as np
# Define grid parameters
REAL_X_POS_START = 164.991
REAL_Y_POS_START = 560.071

REAL_X_POS_END = -139.861
REAL_Y_POS_END = 787.229

SPACING = 27.5  # mm

# Calculate the number of columns and rows
num_cols = int((REAL_X_POS_START - REAL_X_POS_END) // SPACING) + 1
num_rows = int((REAL_Y_POS_END - REAL_Y_POS_START) // SPACING) + 1

print("number of cols", num_cols)
print("number of rows", num_rows)
# Generate grid points
grid_points = []

for row in range(num_rows):
    y = REAL_Y_POS_START + row * SPACING
    for col in range(num_cols):
        x = REAL_X_POS_START - col * SPACING
        grid_points.append((round(x, 3), round(y, 3)))

# Print the results
# for point in grid_points:
#     print(f"{point[0]},{point[1]}")

np.savetxt('output/fixed_robot.csv', grid_points, delimiter=',', fmt='%d')


