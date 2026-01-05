import sys
import os
import json
import time
from geotoolkit.io import read_geojson, write_geojson, write_csv  # <--- [新增] 引入 write_csv
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest, get_area, get_length, is_contained
from geotoolkit.viz import plot_features

# ==========================================
# 1. 全局准备阶段
# ==========================================
print("正在初始化数据，请稍候...")
try:
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
    
    # 简单的交互：允许用户输入距离
    user_dist = input("请输入缓冲区距离 (米，默认500): ").strip()
    dist = float(user_dist) if user_dist.isdigit() else 500
    
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
    """功能 5: 可视化结果 (智能版)"""
    print("\n>>> 正在执行 [5] 生成可视化图表...")
    
    viz_features = []
    title = ""
    path_clip = "out/clipped_features.geojson"
    path_buf = "out/buffer_500m.geojson"
    
    if os.path.exists(path_clip):
        print(f" -> [展示] 检测到裁剪结果: {path_clip}")
        try:
            with open(path_clip, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: viz_features.extend(data["features"])
                title = "Clipped Features Result"
        except Exception: pass

    elif os.path.exists(path_buf):
        print(f" -> [展示] 检测到缓冲区文件: {path_buf}")
        try:
            with open(path_buf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: viz_features.extend(data["features"])
                elif "type" in data and data["type"] == "Polygon":
                     viz_features.append({"type": "Feature", "properties": {"type": "Buffer"}, "geometry": data})
                title = "Buffer Analysis Result"
        except Exception: pass

    else:
        print(" -> 未找到处理结果，展示原始数据...")
        viz_features.extend(fc_m["features"])
        title = "Original Data (No Processing)"

    if "Buffer" in title:
        viz_features.append({"type": "Feature", "geometry": poly, "properties": {"type": "Original"}})
    if "Buffer" in title or "Clipped" in title:
         points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]
         viz_features.extend(points)

    output_file = "out/visualization_result.png"
    try:
        plot_features({"type": "FeatureCollection", "features": viz_features}, title=title, output_path=output_file)
        if sys.platform == "win32": os.startfile(os.path.abspath(output_file))
    except Exception as e:
        print(f" [错误] 绘图失败: {e}")

# --- [新增] 功能 6: 生成报表 ---
def task_report():
    """功能 6: 生成 Excel/CSV 报表"""
    print("\n>>> 正在执行 [6] 生成距离报表...")
    
    report_data = []
    
    # 1. 找到所有的点
    points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]
    
    # 2. 临时生成一个 500m 缓冲区用来判断“是否在内部”
    temp_buf = buffer(poly, 500)
    
    print(f" -> 正在计算 {len(points)} 个点到多边形的距离...")
    
    for i, pt_feature in enumerate(points):
        geom = pt_feature["geometry"]
        
        # 计算距离
        d, _, _ = nearest(geom, poly)
        
        # 判断是否在缓冲区内
        in_buf = is_contained(temp_buf, geom)
        
        # 收集一行数据
        row = {
            "ID": i + 1,
            "Type": "Point",
            "Distance_to_Polygon (m)": round(d, 2), # 距离保留两位小数
            "Inside_Buffer_500m": "Yes" if in_buf else "No" # 把 True/False 变成 Yes/No 更好看
        }
        report_data.append(row)
        
    # 3. 导出
    csv_path = "out/distance_report.csv"
    write_csv(report_data, csv_path)
    
    # 尝试自动打开 CSV (仅限 Windows)
    if sys.platform == "win32":
        try:
            os.startfile(os.path.abspath(csv_path))
        except:
            pass

# ==========================================
# 3. 菜单配置
# ==========================================

MENU = {
    "1": ("生成缓冲区 (Buffer)", task_buffer),
    "2": ("裁剪要素 (Clip)", task_clip),
    "3": ("计算最近距离 (Nearest)", task_nearest),
    "4": ("几何属性检查 (Analysis)", task_analysis),
    "5": ("可视化结果 (Visualize)", task_viz),
    "6": ("生成报表 (Export CSV) [NEW!]", task_report) # <--- 新增菜单项
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
        
        user_input = input("请输入功能序号 (多选如 '1,6'): ").strip()
        
        if user_input in ['0', 'q', 'exit', 'quit']:
            print("正在退出程序...")
            break
        if not user_input: continue

        selection_keys = user_input.replace("，", ",").replace(",", " ").split()
        
        valid_choice = False
        for key in selection_keys:
            if key in MENU:
                valid_choice = True
                try:
                    MENU[key][1]() 
                except Exception as e:
                    print(f"[错误] 执行出错: {e}")
            else:
                if key != '0': print(f"\n[警告] 序号 '{key}' 无效。")
        
        if valid_choice:
            input("\n任务执行完毕，按 [回车键] 返回菜单...")
            
    print("再见！")