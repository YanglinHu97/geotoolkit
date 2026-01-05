import sys
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
# 引入所有功能（包含你刚才可能添加的新功能）
from geotoolkit.analysis import buffer, clip, nearest, get_area, get_length, is_contained

print("正在初始化数据，请稍候...")

# ==========================================
# 1. 公共准备阶段 (无论选什么功能都需要这步)
# ==========================================
try:
    # 加载数据
    fc = read_geojson("data/sample.geojson")
    # 投影转换 (WGS84 -> EPSG:3857)
    fc_m = to_epsg(fc, 4326, 3857)
    
    # 提取多边形和点
    poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
    pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]
    print("数据加载与转换完成。\n")
except Exception as e:
    print(f"初始化失败: {e}")
    sys.exit(1)

# ==========================================
# 2. 定义功能函数 (把逻辑封装起来)
# ==========================================

def task_buffer():
    """功能 1: 生成缓冲区"""
    print("\n--- [1] 执行缓冲区分析 ---")
    dist = 500
    buf = buffer(poly, dist)
    write_geojson(buf, "out/buffer_500m.geojson")
    print(f"已生成 {dist}米 缓冲区，保存至 out/buffer_500m.geojson")
    # 这里顺便把刚才的新功能加上
    print(f"缓冲区面积: {get_area(buf):.2f} 平方米")
    return buf # 返回给其他函数用

def task_clip():
    """功能 2: 裁剪要素"""
    print("\n--- [2] 执行裁剪操作 ---")
    # 为了演示，我们需要先有一个缓冲区作为裁剪框
    # 这里我们临时生成一个，或者复用上面的逻辑
    clipper = buffer(poly, 500) 
    clipped = clip(fc_m, clipper)
    write_geojson(clipped, "out/clipped_features.geojson")
    print("裁剪完成，结果保存至 out/clipped_features.geojson")

def task_nearest():
    """功能 3: 计算最近距离"""
    print("\n--- [3] 计算最近距离 ---")
    dist, a, b = nearest(pt, poly)
    print(f"点到多边形的最近距离: {dist:.2f} 米")

def task_analysis():
    """功能 4: 几何属性检查 (新功能)"""
    print("\n--- [4] 几何属性检查 ---")
    # 生成一个临时缓冲区用来测试
    temp_buf = buffer(poly, 500)
    
    perimeter = get_length(temp_buf)
    is_inside = is_contained(temp_buf, pt)
    
    print(f"缓冲区周长: {perimeter:.2f} 米")
    print(f"原始点是否在缓冲区内: {is_inside}")

# ==========================================
# 3. 菜单配置
# ==========================================

# 建立 序号 -> (描述, 函数) 的映射关系
MENU = {
    "1": ("生成缓冲区 (Buffer)", task_buffer),
    "2": ("裁剪要素 (Clip)", task_clip),
    "3": ("计算最近距离 (Nearest)", task_nearest),
    "4": ("几何属性检查 (Analysis)", task_analysis)
}

# ==========================================
# 4. 主运行逻辑 (交互界面)
# ==========================================

if __name__ == "__main__":
    print("="*30)
    print("   GeoToolkit 功能选择菜单")
    print("="*30)
    
    # 打印菜单
    for key, (desc, _) in MENU.items():
        print(f" {key}. {desc}")
    print("="*30)
    print("提示：输入序号执行，多选请用逗号或空格分隔 (例如: 1,3)")
    
    # 获取输入
    user_input = input("\n请选择要执行的功能序号: ").strip()
    
    if not user_input:
        print("未选择任何功能，程序退出。")
        sys.exit()

    # 处理输入 (把 "1,3" 或 "1 3" 变成列表 ['1', '3'])
    # 1. 把中文逗号换成英文逗号
    # 2. 把逗号换成空格
    # 3. 按空格分割
    selection_keys = user_input.replace("，", ",").replace(",", " ").split()
    
    # 执行循环
    for key in selection_keys:
        if key in MENU:
            func_name = MENU[key][0]
            func_to_run = MENU[key][1]
            try:
                func_to_run() # 运行对应的函数
            except Exception as e:
                print(f"执行功能 [{func_name}] 时出错: {e}")
        else:
            print(f"\n[警告] 序号 '{key}' 无效，已跳过。")
            
    print("\n所有任务执行完毕。")