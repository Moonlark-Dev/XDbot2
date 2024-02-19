from PIL import Image
import random


def add_noise(image: Image) -> None:
    width, height = image.size
    num_regions_x = width // 16
    num_regions_y = height // 16

    for i in range(num_regions_x):
        for j in range(num_regions_y):
            x = i * 16
            y = j * 16
            pixel_x = x + random.randint(0,16)
            pixel_y = y + random.randint(0,16)
            # 获取当前像素的RGB值
            r, g, b = image.getpixel((pixel_x, pixel_y))
            # 添加噪点
            noise = random.randint(-20, 20)
            r += noise
            g += noise
            b += noise
            # 限制RGB值在0-255范围内
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            # 设置当前像素的RGB值
            image.putpixel((pixel_x, pixel_y), (r, g, b))

