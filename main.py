import argparse
import numpy as np
import cv2 as cv
from typing import List


def tile_intensity(tile):
    return np.sum((np.sum(tile, 0)), 0)


class Tile:
    def __init__(self, x_start, x_end, y_start, y_end, dots=0, image=None) -> None:
        self.image = image
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.dots = dots
        self.shape = (x_end - x_start, y_end - y_start)

    def draw_cicles(self, image: np.array, radius: int, spacing: int):
        x = self.x_start + spacing + radius
        y = self.y_start + spacing + radius
        white = 255
        for _ in range(self.dots):
            image = cv.circle(image, (y, x), radius, white, -1)
            x += radius + spacing
            if x > self.x_end:
                y += radius + spacing
                x = self.x_start + spacing + radius
                if y > self.y_end:
                    print('dot out of tile bounds!')
                    return image
        return image

    def draw_tile_bounds(self, image):
        return cv.rectangle(image, (self.x_start, self.x_end), (self.y_start, self.y_end), 255, 1)


class DotTransformer:
    def __init__(self, radius=10, spacing=2) -> None:
        self.radius = radius
        self.spacing = spacing

    def divide(self, tile: Tile, dividing_factor=2) -> List[Tile]:
        """
        divide a tile into four smaller tiles, 
        assign a dot value to each tile based on its intensity 
        and the total number of dots for the initial tile,
        TODO: separate dividing factor for x and y
        """
        # if tile.dots <= threshold:
        #     return [tile]
        # if tile.size[0] <= self.radius + self.spacing or tile.size[1] <= self.radius + self.spacing:
        #     return [tile]

        sub_tiles = []
        # I'm guissing sometimes the loop won't iterate over the whole tile
        # and as a result a some intensity (dots) might be lost
        # but it should be very minimal and non-important
        total_intensity = tile_intensity(tile.image)
        for x in range(dividing_factor):
            x_step_size = int(tile.shape[0]/dividing_factor)
            x_start = x * x_step_size
            x_end = x_start + x_step_size
            for y in range(dividing_factor):
                y_step_size = int(tile.shape[1]/dividing_factor)
                y_start = y * y_step_size
                y_end = y_start + y_step_size

                image = tile.image[x_start:x_end, y_start:y_end]
                sub_tile_intensity = tile_intensity(image)
                sub_tile_dots = int(
                    tile.dots * (sub_tile_intensity/total_intensity))
                sub_tile = Tile(x_start + tile.x_start, x_end + tile.x_start,
                                y_start + tile.y_start, y_end + tile.y_start, sub_tile_dots, image)
                sub_tiles.append(sub_tile)

        return sub_tiles

    def recursive_tiling(self, tile: Tile, dot_threshold=4, size_threshold=14, dividing_factor=2):
        print((tile.x_start, tile.x_end, tile.y_start, tile.y_end))
        if tile.dots <= dot_threshold:
            return [tile]
        if tile.shape[0] <= size_threshold or tile.shape[1] <= size_threshold:
            return [tile]

        sub_tiles = self.divide(tile)
        results = []
        for sub_tile in sub_tiles:
            results += self.recursive_tiling(sub_tile)
        print('---')
        return results


if __name__ == '__main__':
    image_path = './1.jpg'
    image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    image = np.ones(image.shape) * 255 - image
    image = cv.convertScaleAbs(image, alpha=1.5, beta=0)
    new_image = np.zeros(image.shape)
    main_tile = Tile(
        x_start=0, x_end=image.shape[0], y_start=0, y_end=image.shape[1], dots=10000, image=image)
    transformer = DotTransformer(radius=5, spacing=1)
    tiles = transformer.recursive_tiling(main_tile)
    print(len(tiles))
    for tile in tiles:
        new_image = tile.draw_cicles(new_image, 2, 3)
        # new_image = tile.draw_tile_bounds(new_image)
    cv.imshow('new_image', new_image)
    cv.waitKey(0)
