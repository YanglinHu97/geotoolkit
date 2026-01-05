import sys
import os
import json  # <--- 之前缺少的工具库，现在加上了
import time
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest, get_area, get_length, is_contained
from geotoolkit.viz import plot_features

# ==========================================
# 1. 全局准备阶段
# ==========================================
print("正在初始化数据，请稍候...")
try:
    # 确保输出目录存在
    if not os.path.exists("out"):
        os.makedirs("out")
        
    fc = read_geojson("data/sample.geojson")
    fc_m = to_epsg(fc, 4326, 3857)
    
    poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
    pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]
    print("数据加载与转换完成。")
except Exception as e:
    print(f"初始化失败: {e}")
    sys.exit(1)

# ==========================================
# 2. 定义功能函数
# ==========================================

def task_buffer():
    """功能 1: 生成缓冲区"""
    print("\n>>> 正在执行 [1] 缓冲区分析...")
    dist = 500
    buf = buffer(poly, dist)
    write_geojson(buf, "out/buffer_500m.geojson")
    print(f" -> 已生成 {dist}米 缓冲区，保存至 out/buffer_500m.geojson")
    print(f" -> 缓冲区面积: {get_area(buf):.2f} 平方米")
    return buf

def task_clip():
    """功能 2: 裁剪要素"""
    print("\n>>> 正在执行 [2] 裁剪操作...")
    clipper = buffer(poly, 500) 
    clipped = clip(fc_m, clipper)
    write_geojson(clipped, "out/clipped_features.geojson")
    print(" -> 裁剪完成，结果保存至 out/clipped_features.geojson")

def task_nearest():
    """功能 3: 计算最近距离"""
    print("\n>>> 正在执行 [3] 计算最近距离...")
    dist, a, b = nearest(pt, poly)
    print(f" -> 点到多边形的最近距离: {dist:.2f} 米")

def task_analysis():
    """功能 4: 几何属性检查"""
    print("\n>>> 正在执行 [4] 几何属性检查...")
    temp_buf = buffer(poly, 500)
    perimeter = get_length(temp_buf)
    is_inside = is_contained(temp_buf, pt)
    print(f" -> 缓冲区周长: {perimeter:.2f} 米")
    print(f" -> 原始点是否在缓冲区内: {is_inside}")

def task_viz():
    """功能 5: 可视化结果 (超级智能版：支持裁剪和缓冲区文件)"""
    print("\n>>> 正在执行 [5] 生成可视化图表...")
    
    viz_features = []
    title = "Visualization"
    
    # 路径定义
    path_clip = "out/clipped_features.geojson"
    path_buf = "out/buffer_500m.geojson" # 功能 1 的输出文件
    
    # --- 逻辑判断开始 ---
    
    # 1. 优先检查：是否有裁剪结果 (功能 2)
    if os.path.exists(path_clip):
        print(f" -> [优先展示] 检测到裁剪结果: {path_clip}")
        try:
            with open(path_clip, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data:
                    viz_features.extend(data["features"])
                title = "Clipped Features Result"
        except Exception as e:
            print(f" [警告] 读取失败: {e}")

    # 2. 其次检查：是否有缓冲区文件 (功能 1)
    # 注意：使用 elif，意味着如果上面展示了裁剪，这里就不重复展示缓冲区了，避免图形重叠太乱
    elif os.path.exists(path_buf):
        print(f" -> [展示] 检测到缓冲区文件: {path_buf}")
        try:
            with open(path_buf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # buffer 函数返回的是 Geometry，read_geojson 读取后也是单纯的 dict
                # 如果是直接由 write_geojson 写的，通常是 GeoJSON 结构
                # 无论它是 FeatureCollection 还是 Geometry，我们都做个兼容处理
                
                if "features" in data: # 如果是 FeatureCollection
                    viz_features.extend(data["features"])
                elif "type" in data and data["type"] == "Polygon": # 如果纯几何
                     viz_features.append({
                        "type": "Feature",
                        "properties": {"source": "Task 1 File"},
                        "geometry": data
                    })
                title = "Buffer Analysis (From Task 1)"
        except Exception as e:
             print(f" [警告] 读取失败: {e}")

    # 3. 如果啥都没找到 (用户只运行了 5)
    else:
        print(" -> 未找到任何历史结果，正在实时生成预览...")
        buf_geom = buffer(poly, 500)
        viz_features.append({
            "type": "Feature",
            "properties": {"source": "On-the-fly"},
            "geometry": buf_geom
        })
        title = "Buffer Preview (Default)"

    # --- 公共部分：总是加上原始点 ---
    points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]
    viz_features.extend(points)

    # --- 绘图 ---
    viz_data = {
        "type": "FeatureCollection",
        "features": viz_features
    }
    
    output_file = "out/visualization_result.png"
    try:
        plot_features(viz_data, title=title, output_path=output_file)
        if sys.platform == "win32":
            os.startfile(os.path.abspath(output_file))
    except Exception as e:
        print(f" [错误] 绘图失败: {e}")

# ==========================================
# 3. 菜单配置
# ==========================================

MENU = {
    "1": ("生成缓冲区 (Buffer)", task_buffer),
    "2": ("裁剪要素 (Clip)", task_clip),
    "3": ("计算最近距离 (Nearest)", task_nearest),
    "4": ("几何属性检查 (Analysis)", task_analysis),
    "5": ("可视化结果 (Visualize)", task_viz)
}

# ==========================================
# 4. 主循环逻辑
# ==========================================

if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print("      GeoToolkit 交互式控制台")
        print("="*40)
        
        for key, (desc, _) in MENU.items():
            print(f" [{key}] {desc}")
        print(" [0] 退出程序 (Exit)")
        print("-" * 40)
        
        user_input = input("请输入功能序号 (多选如 '1,5'): ").strip()
        
        if user_input in ['0', 'q', 'exit', 'quit']:
            print("正在退出程序...")
            break
        
        if not user_input:
            continue

        selection_keys = user_input.replace("，", ",").replace(",", " ").split()
        
        valid_choice = False
        for key in selection_keys:
            if key in MENU:
                valid_choice = True
                func_name = MENU[key][0]
                try:
                    MENU[key][1]() # 运行函数
                except Exception as e:
                    print(f"[错误] 执行 '{func_name}' 时出错: {e}")
            else:
                if key != '0':
                    print(f"\n[警告] 序号 '{key}' 无效。")
        
        if valid_choice:
            input("\n任务执行完毕，按 [回车键] 返回菜单...")
            
    print("再见！")