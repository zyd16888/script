from PIL import Image, ImageDraw, ImageFont
import math

def create_badge(
    text: str,
    text_color: str = "#FFFFFF",
    bg_color: str = "#666666",
    angle: float = -15,
    font_size: int = 240,
    padding: int = 10
) -> Image:
    """
    创建带有倾斜文字的透明背景标签
    
    参数:
        text: 要显示的文字
        text_color: 文字颜色（十六进制颜色代码）
        bg_color: 文字背景颜色（十六进制颜色代码）
        angle: 倾斜角度（度数）
        font_size: 字体大小
        padding: 文字周围的内边距
    """
    # 使用2倍的尺寸进行渲染，以提高清晰度
    scale_factor = 6
    font_size = font_size * scale_factor
    padding = padding * scale_factor
    
    # 创建字体对象
    font = ImageFont.truetype("D:\\project\\python\\qqmusic_download\\fonts\\可爱泡芙桃子酒.ttf", font_size)
    
    # 计算文字大小
    dummy_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 计算旋转后的尺寸
    angle_rad = math.radians(angle)
    rotated_width = abs(text_width * math.cos(angle_rad)) + abs(text_height * math.sin(angle_rad))
    rotated_height = abs(text_width * math.sin(angle_rad)) + abs(text_height * math.cos(angle_rad))
    
    # 创建透明背景图片（使用更高分辨率）
    image_width = int(rotated_width + 2 * padding)
    image_height = int(rotated_height + 2 * padding)
    image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    
    # 创建文字背景
    bg_layer = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), bg_color)
    bg_layer = bg_layer.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0), resample=Image.BICUBIC)
    
    # 将背景层粘贴到主图层
    image.paste(bg_layer, (0, 0), bg_layer)
    
    # 创建文字层（使用RGBA模式以支持抗锯齿）
    text_layer = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    
    # 计算文字绘制位置，考虑基线偏移
    x = padding - text_bbox[0]  # 补偿左边界偏移
    y = padding - text_bbox[1]  # 补偿上边界偏移
    text_draw.text((x, y), text, font=font, fill=text_color)
    
    text_layer = text_layer.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0), resample=Image.BICUBIC)
    
    # 将文字层粘贴到主图层
    image.paste(text_layer, (0, 0), text_layer)
    
    # 将图像缩放回原始大小
    final_width = int(image_width / scale_factor)
    final_height = int(image_height / scale_factor)
    image = image.resize((final_width, final_height), Image.LANCZOS)
    
    return image

# 使用示例
if __name__ == "__main__":
    # 创建标签
    badge = create_badge(
        text="中字去码",
        text_color="#FFFFFF",
        bg_color="#3CB371",
        angle=45
    )
    
    # 保存图片
    badge.save("badge.png")