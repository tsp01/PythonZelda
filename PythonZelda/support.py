import pygame
from csv import reader
from os import walk

def import_csv_layout(path):
    """
    reads csv files and returns them as lists
    """
    
    terrain_map = []

    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

def import_folder(path):
    """
    reads folders and returns all image files in a list
    """

    surface_list = []
    # reg_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # reg_list.append(full_path)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    # print(reg_list)

    return surface_list


