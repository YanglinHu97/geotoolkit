import sys
import time
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
# 引入所有功能
from geotoolkit.analysis import buffer, clip, nearest, get_area, get_length, is_contained

# ==========================================
# 1. 全局准备阶段 (只在程序启动时运行一次)
# ==========================================
print("正在初始化数据，请稍候...")
try:
    # 加载数据
    fc = read_geojson("data/sample.geojson")
    # 投影转换 (WGS84 -> EPSG:3857)
    fc_m = to_epsg(fc, 4326, 3857)
    
    # 提取多边形和点
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

# ==========================================
# 3. 菜单配置
# ==========================================

MENU = {
    "1": ("生成缓冲区 (Buffer)", task_buffer),
    "2": ("裁剪要素 (Clip)", task_clip),
    "3": ("计算最近距离 (Nearest)", task_nearest),
    "4": ("几何属性检查 (Analysis)", task_analysis)
}

# ==========================================
# 4. 主循环逻辑 (核心修改部分)
# ==========================================

if __name__ == "__main__":
    while True:
        # 打印漂亮的菜单头
        print("\n" + "="*40)
        print("      GeoToolkit 交互式控制台")
        print("="*40)
        
        # 动态打印菜单选项
        for key, (desc, _) in MENU.items():
            print(f" [{key}] {desc}")
        print(" [0] 退出程序 (Exit)")
        print("-" * 40)
        
        # 获取用户输入
        user_input = input("请输入功能序号 (多选如 '1,3'): ").strip()
        
        # 检查是否退出
        if user_input in ['0', 'q', 'exit', 'quit']:
            print("正在退出程序...")
            break
        
        if not user_input:
            continue # 如果直接按回车，就重新显示菜单

        # 处理多选输入 (支持中文逗号、英文逗号、空格)
        selection_keys = user_input.replace("，", ",").replace(",", " ").split()
        
        # 执行选中的功能
        valid_choice = False
        for key in selection_keys:
            if key in MENU:
                valid_choice = True
                func_name = MENU[key][0]
                func_to_run = MENU[key][1]
                try:
                    func_to_run() # 运行函数
                except Exception as e:
                    print(f"[错误] 执行 '{func_name}' 时出错: {e}")
            else:
                if key != '0':
                    print(f"\n[警告] 序号 '{key}' 无效。")
        
        # 暂停，让用户有机会看清结果
        if valid_choice:
            input("\n任务执行完毕，按 [回车键] 返回菜单...")
        
    print("再见！")