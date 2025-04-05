import cv2
import numpy as np

# 读取图像
image_path = 'assets/competing.png'
image = cv2.imread(image_path)

# 检查图像是否成功加载
if image is None:
    raise FileNotFoundError(f"Image not found at {image_path}")

# 转换为HSV格式
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 设置V的阈值为80，创建掩膜
v_threshold = 120
_, _, v_channel = cv2.split(hsv_image)
mask = cv2.inRange(v_channel, 0, v_threshold)

# 保存或显示掩膜
cv2.imwrite('assets/competing_mask.png', mask)
# 如果需要显示掩膜，可以使用以下代码
cv2.imshow('Mask', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()