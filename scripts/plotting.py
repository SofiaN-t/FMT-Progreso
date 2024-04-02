import rasterio 
from rasterio.plot import show
import numpy as np

# 1.
# Plot on earth's surface
# When you want to plot the full dataset
        
# Plot band1 with geographic coordinates
raster_file_path = "C:\\Users\\user\\Documents\\EAE\\peru_decrease_2004_01_01_to_2023_01_01.asc"
with rasterio.open(raster_file_path) as src:
    # Read the raster data
    data = src.read(1) 
    plt.figure(figsize=(10, 10))
    show(data, transform=src.transform)
    # plt.title('2023')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.savefig('data/download/output/peru_all_years_no_colormap.png')
    # plt.show()
    ### plt additions seem not to be integrated


# Plot on earth's surface when you are zooming in specific values
# Zoom-in to 2004
specific_value = 2004

# Open the raster file
with rasterio.open(raster_file_path) as src:
    # Read the first band
    band1 = src.read(1)

    # Zoom-in for plotting
    rows, cols = np.where(band1 == 2004)
    margin = 10  # This sets a margin of 10 pixels
    row_min, row_max = rows.min(), rows.max()
    col_min, col_max = cols.min(), cols.max()
    
    # Create a mask for the specific value
    specific_value_mask = band1 == specific_value
    
    # Create a masked array where non-matching values are set to NaN
    masked_band1 = np.where(specific_value_mask, band1, np.nan)

    # Translation to spatial coordinates
    transform = src.transform
    top_left = transform * (col_min, row_min)
    bottom_right = transform * (col_max, row_max)

    # Plot the masked array with geographic coordinates
    plt.figure(figsize=(10, 10))
    show(masked_band1, transform=transform, cmap='viridis') #, crs=src.crs
    plt.title(f'Plot of Specific Value ({specific_value}) on Earth\'s Surface')
    plt.xlim([top_left[0], bottom_right[0]])
    plt.ylim([bottom_right[1], top_left[1]])
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()
    ### The plot seems to have a blank background
    ## Resolution issue? -- Have added limits in-between

# Let's take some steps to double-check
import matplotlib.pyplot as plt

# Directly visualize the data for testing purposes
# Zoom-in for plotting
# rows, cols = np.where(band1 == 2004)
# margin = 10
# row_min, row_max = rows.min(), rows.max()
# col_min, col_max = cols.min(), cols.max()
# img = plt.imshow(band1 == 2004, extent = src.bounds, cmap='viridis') # viridis adds a blank background?
# plt.colorbar(img)
plt.imshow(band1 == 2004) # imshow from matplotlib has access to extent variable, hence transform will not be used
plt.colorbar()
plt.title("Presence of 2004 in band1")
plt.xlim(col_min - margin, col_max + margin)
plt.ylim(row_max + margin, row_min - margin)
plt.show()

## Let's use this plotting method and not the show from rasterio
with rasterio.open(raster_file_path) as src:
    # Read the first band
    band1 = src.read(1)
    # Apply the mask for the year 2004
    masked_band1 = np.where(band1 == 2004, band1, np.nan) # second argument = band1/1
    # Determine the spatial extent of the entire dataset
    left, bottom, right, top = src.bounds
    # Now, calculate the spatial extent of the area of interest based on the row and column indices
    # Get the spatial coordinates of the top left and bottom right corners of the bounding box
    # using the affine transformation from the rasterio dataset
    top_left_x, top_left_y = src.transform * (col_min, row_min)
    bottom_right_x, bottom_right_y = src.transform * (col_max, row_max)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 10))
    img = ax.imshow(masked_band1, cmap='viridis', extent=(left, right, bottom, top))
    plt.colorbar(img, label='Year of Tree Cover Loss')

    # Set the x and y axis limits to the bounding box of the year 2004 data to zoom in
    ax.set_xlim(left=top_left_x, right=bottom_right_x)
    ax.set_ylim(bottom=bottom_right_y, top=top_left_y)

    plt.title('Tree Cover Loss in 2004')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()
    ### Colorbar is incomprehensible, limits are still off

# Alternatively,
with rasterio.open(raster_file_path) as src:
    band1 = src.read(1)
    
    # Create a mask for the year 2004, setting non-matching values to NaN
    masked_band1 = np.where(band1 == 2004, 1, np.nan)  # Use 1 for visible, NaN for invisible

    # Now plot using imshow with the extent
    plt.imshow(masked_band1, cmap='viridis', extent=src.bounds, interpolation='none')
    plt.colorbar(label='Tree Cover Loss in 2004')
    
    # Potentially update xlim and ylim to the exact bounding box where data is present
    # Use the transform to get the spatial extent of the non-NaN data
    rows, cols = np.where(band1 == 2004)
    if rows.size > 0 and cols.size > 0:
        row_min, row_max = np.min(rows), np.max(rows)
        col_min, col_max = np.min(cols), np.max(cols)

        # Get spatial coordinates for plotting extent
        left, top = src.transform * (col_min, row_min)
        right, bottom = src.transform * (col_max, row_max)

        plt.xlim(left, right)
        plt.ylim(bottom, top)
    
    plt.title('Tree Cover Loss in 2004')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()


# Adjust the extent and colorbar
with rasterio.open(raster_file_path) as src:
    # Read the first band
    band1 = src.read(1)
    
    # Create a mask for the year 2004, setting non-matching values to NaN
    masked_band1 = np.where(band1 == 2004, 1, 0)  # Use 1 for visible, 0 for invisible
    
    # Calculate the bounds of the area where 2004 is present
    rows, cols = np.where(band1 == 2004)
    if rows.size > 0 and cols.size > 0:
        row_min, row_max = np.min(rows), np.max(rows)
        col_min, col_max = np.min(cols), np.max(cols)
        
        # Use the affine transformation to convert array indices to spatial coordinates
        left, top = src.transform * (col_min, row_min)
        right, bottom = src.transform * (col_max, row_max)
        
        # Calculate the center of the bounding box and set a buffer around it
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        buffer = max(right - left, top - bottom) * 0.5  # Dynamic buffer size

    # Plot the data with adjusted bounds
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust figure size as needed
    img = ax.imshow(masked_band1, cmap='viridis', extent=src.bounds, interpolation='none')
    
    # Set the color bar to indicate presence or absence of the 2004 data
    cbar = plt.colorbar(img, ticks=[0, 1], shrink=0.5)  # Shrink color bar to fit
    cbar.ax.set_yticklabels(['No data', 'Tree Cover Loss 2004'])  # Set custom labels

    # Use the calculated center and buffer to set the plot limits, to zoom in on the data
    ax.set_xlim(center_x - buffer, center_x + buffer)
    ax.set_ylim(center_y - buffer, center_y + buffer)

    plt.title('Tree Cover Loss in 2004')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig('data/download/output/peru_2004_tight_bounds_purple_background.png')
    plt.show()

# Try to fix the blank background
from matplotlib.colors import ListedColormap
# Define a new colormap with the first color (for 0) set as black
# and the second color (for 1) set to a color that will represent tree cover loss
new_cmap = ListedColormap(['black', 'red'])

with rasterio.open(raster_file_path) as src:
    band1 = src.read(1)
    masked_band1 = np.where(band1 == 2004, 2004, -9999)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 5))
    img = ax.imshow(masked_band1, cmap=new_cmap, extent=src.bounds, interpolation='none')

    # Create a color bar with a new label
    cbar = plt.colorbar(img, ticks=[-9999, 2004], shrink=0.5)  # Only one tick for the value 1
    cbar.ax.set_yticklabels(['No value data','Tree Cover Loss 2004'])  # Label for the tick

    # Set plot title and labels
    plt.title('Tree Cover Loss in 2004')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig('data/download/output/peru_2004_black_background.png')
    plt.show()

# What about the last three available years?
new_cmap = ListedColormap(['black', 'yellow', 'orange', 'red'])
with rasterio.open(raster_file_path) as src:
    band1 = src.read(1)
    mask_2021 = band1 == 2021
    mask_2022 = band1 == 2022
    mask_2023 = band1 == 2023

    combined_mask = mask_2021 | mask_2022 | mask_2023

    combined_mask_band = np.where(combined_mask, band1, -9999)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 5))
    img = ax.imshow(combined_mask_band, cmap=new_cmap, extent=src.bounds, interpolation='none')

    # Create a color bar with a new label
    cbar = plt.colorbar(img, ticks=[-9999, 2021, 2022, 2023], shrink=0.5)
    cbar.ax.set_yticklabels(['No value data', '2021', '2022', '2023'])  # Label for the tick

    # Set plot title and labels
    plt.title('Tree Cover Loss')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.savefig('data/download/output/peru_last_years_black_background.png')
    plt.show()

### Basis look ok, but only red points -- ? -- Let's try to  refine
    
# Custom colormap
new_cmap = ListedColormap(['black', 'yellow', 'orange', 'red'])

# Define a nodata value that is not in the range of your actual data
nodata_value = -9999

with rasterio.open(raster_file_path) as src:
    band1 = src.read(1)

    # Initialize combined_mask_band with nodata values
    combined_mask_band = np.full(band1.shape, nodata_value)

    # Now, instead of using a boolean mask, directly set the year values
    combined_mask_band[band1 == nodata_value] = 0    
    combined_mask_band[band1 == 2021] = 1
    combined_mask_band[band1 == 2022] = 2
    combined_mask_band[band1 == 2023] = 3

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 5))
    img = ax.imshow(combined_mask_band, cmap=new_cmap, extent=src.bounds, interpolation='none')

    # img.set_clim(0.5, 3.5)

    # Set colorbar ticks and labels
    cbar = plt.colorbar(img, shrink=0.5)
    cbar.set_ticks([0, 1, 2, 3])
    cbar.ax.set_yticklabels(['No data value', '2021', '2022', '2023'])
    # Set colorbar for nodata_value
    # cbar.cmap.set_under('black')

    # Set plot title and labels
    ax.set_title('Tree Cover Loss')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    plt.show()

