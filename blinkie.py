#!/usr/bin/env python3
# imageio for giffing
import sys

from PIL import Image, ImageColor, ImageDraw, ImageFont
from webcolors import name_to_rgb


def make_gif(word, rgb_color, text_color, text_blink_color):
    images = []
    
    font = ImageFont.truetype('REDENSEK.TTF', 13)

    letter_sizes = [font.getsize(l) for l in word]
    widths, heights = zip(*letter_sizes)

    height = max(heights)
    width = sum(widths) + (len(widths) - 1) * 3 + 4

    worst_magenta = (255, 0, 255)
    base_image = Image.new('P', (width, height), color=worst_magenta)
    base_draw = ImageDraw.Draw(base_image)

    black = (0, 0, 0, 255)
    white = (255, 255, 255, 255)
    # calculate shading
    # this would probably look BETTER if it were ratioed instead of absolute,
    # but it's actually not fucking bad
    shading = (max(rgb_color[0] - 96, 0),
               max(rgb_color[1] - 96, 0),
               max(rgb_color[2] - 96, 0),
               255)
    highlight = (min(rgb_color[0] + 96, 255),
                 min(rgb_color[1] + 96, 255),
                 min(rgb_color[2] + 96, 255),
                 255)

    def draw_box(draw, offset, top_color, bottom_color, font_color):
        draw.rectangle((offset - 2, 0, offset + widths[i] + 1, height - 1), outline=black, fill=rgb_color + (255,))
        # erase the corners
        draw.point((offset - 2, 0), fill=worst_magenta)
        draw.point((offset - 2, height - 1), fill=worst_magenta)
        draw.point((offset + widths[i] + 1, 0), fill=worst_magenta)
        draw.point((offset + widths[i] + 1, height - 1), fill=worst_magenta)

        # add character
        draw.text((offset, -3), letter, font=font, fill=font_color)

        # dark top_color along the bottom and right sides
        draw.line((offset + widths[i], 1, offset + widths[i], height - 2), fill=top_color, width=1)
        draw.line((offset - 1, height - 2, offset + widths[i], height - 2), fill=top_color, width=1)
        # bottom_color along the top and left sides
        draw.line((offset - 1, 1, offset - 1, height - 3), fill=bottom_color, width=1)
        draw.line((offset - 1, 1, offset + widths[i] - 1, 1), fill=bottom_color, width=1)

    for i, letter in enumerate(word):
        # this is some FIDDLY ASS MATH but hey it works
        # 2 pixels for the first char + 3 pixels in between each following char
        # this is the horizontal offset for the character, not the box
        offset = 2 + sum(widths[:i]) + i * 3
        draw_box(base_draw, offset, shading, highlight, text_color)

    # do it again but build frames 
    for i, letter in enumerate(word):
        images.append(base_image)
        images.append(base_image.copy())
        new_draw = ImageDraw.Draw(images[-1])

        offset = 2 + sum(widths[:i]) + i * 3
        draw_box(new_draw, offset, highlight, shading, text_blink_color)

    all_image = base_image.copy()
    all_draw = ImageDraw.Draw(all_image)
    # final flash
    for i, letter in enumerate(word):
        offset = 2 + sum(widths[:i]) + i * 3
        draw_box(all_draw, offset, highlight, shading, text_blink_color)

    images.append(base_image)
    images.append(all_image)
    images.append(base_image)
    images.append(all_image)
    images.append(base_image)

    return images


def main():
    word = input('Word to blink: ')
    word = word.lower()
    if len(word) > 64:
        print('64 characters should be enough for anybody.')
        return None

    rgb_color = None
    while rgb_color is None:
        color = input('What color? ')
        color = color.lower()
        try:
            rgb_color = name_to_rgb(color)
        except ValueError:
            print('Not a valid color\n')

    text_color = None
    while text_color is None:
        color = input('Text color? ')
        color = color.lower()
        try:
            text_color = name_to_rgb(color)
        except ValueError:
            print('Not a valid color\n')

    text_blink_color = None
    while text_blink_color is None:
        color = input('Text blink color? ')
        color = color.lower()
        try:
            text_blink_color = name_to_rgb(color)
        except ValueError:
            print('Not a valid color\n')

    images = make_gif(word, rgb_color, text_color, text_blink_color)
    images[0].save(f'{word}.gif',
                   save_all=True,
                   append_images=images[1:],
                   duration=300,
                   loop=0,
                   transparency=0) # i do not know. something about the order of colors
    return



if __name__ == "__main__":
    main()
