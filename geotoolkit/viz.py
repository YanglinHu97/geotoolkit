import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # 遍历绘制
    for feature in feature_collection["features"]:
        geom = shape(feature["geometry"])
        geom_type = geom.geom_type
        props = feature.get("properties", {})
        
        # 样式逻辑
        if geom_type == 'Point':
            ax.plot(geom.x, geom.y, 'ro', markersize=6, label='Point', zorder=5)
            
        elif geom_type == 'Polygon':
            x, y = geom.exterior.xy
            # 如果是原始多边形（我们在 demo.py 里标记了 Original），画黑色虚线框
            if props.get("type") == "Original":
                ax.plot(x, y, 'k--', linewidth=1.5, label='Original Polygon')
            else:
                # 缓冲区或普通多边形
                ax.plot(x, y, color='#6699cc', alpha=0.8, linewidth=2)
                ax.fill(x, y, color='#6699cc', alpha=0.3)

    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5) # 开启网格，方便看距离
    
    # --- 新增：添加坐标轴标签 ---
    ax.set_xlabel("X Coordinates (Meters EPSG:3857)", fontsize=10)
    ax.set_ylabel("Y Coordinates (Meters EPSG:3857)", fontsize=10)
    
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f" -> 可视化图片已保存至: {output_path}")