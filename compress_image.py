from PIL import Image
import os

# 讀取原始圖片
img = Image.open('richmenu.png')

# 取得原始大小
original_size = os.path.getsize('richmenu.png')
print(f'原始大小: {original_size / 1024 / 1024:.2f}MB')

# 目標大小為 950KB (留一些緩衝)
target_size = 950 * 1024
current_img = img.copy()

# 先嘗試不同的品質設定
for quality in [85, 75, 65, 55]:
    # 轉換為 RGB (某些 PNG 可能是 RGBA)
    if current_img.mode == 'RGBA':
        # 創建白色背景
        bg = Image.new('RGB', current_img.size, (255, 255, 255))
        # 使用 alpha 通道作為 mask
        bg.paste(current_img, mask=current_img.split()[3])
        current_img = bg
    elif current_img.mode != 'RGB':
        current_img = current_img.convert('RGB')

    # 儲存為 JPEG 格式 (比 PNG 壓縮率更好)
    current_img.save('richmenu_compressed.jpg', 'JPEG',
                     quality=quality, optimize=True)

    compressed_size = os.path.getsize('richmenu_compressed.jpg')
    print(f'品質 {quality}: {compressed_size / 1024:.2f}KB')

    if compressed_size <= target_size:
        print(f'✓ 成功壓縮至目標大小內！')
        break
else:
    # 如果品質調整還不夠，縮小尺寸
    print('\n需要縮小圖片尺寸...')
    scale = 0.9
    while scale > 0.5:
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)

        resized_img = img.resize(
            (new_width, new_height), Image.Resampling.LANCZOS)

        if resized_img.mode == 'RGBA':
            bg = Image.new('RGB', resized_img.size, (255, 255, 255))
            bg.paste(resized_img, mask=resized_img.split()[3])
            resized_img = bg
        elif resized_img.mode != 'RGB':
            resized_img = resized_img.convert('RGB')

        resized_img.save('richmenu_compressed.jpg',
                         'JPEG', quality=75, optimize=True)

        compressed_size = os.path.getsize('richmenu_compressed.jpg')
        print(
            f'尺寸 {new_width}x{new_height} (縮放 {scale:.0%}): {compressed_size / 1024:.2f}KB')

        if compressed_size <= target_size:
            print(f'✓ 成功壓縮至目標大小內！')
            break

        scale -= 0.05

final_size = os.path.getsize('richmenu_compressed.jpg')
print(f'\n最終大小: {final_size / 1024:.2f}KB ({final_size / 1024 / 1024:.2f}MB)')
print('\n壓縮完成！輸出檔案: richmenu_compressed.jpg')
