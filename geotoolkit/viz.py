# geotoolkit/viz.py

import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png"):
    """
    将 GeoJSON FeatureCollection 绘制并保存为图片。
    """
    # 创建画布
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title)
    
    # 遍历所有要素并绘制
    for feature in feature_collection["features"]:
        geom = shape(feature["geometry"])
        geom_type = geom.geom_type
        
        # 1. 如果是点 (Point) -> 画红点
        if geom_type == 'Point':
            ax.plot(geom.x, geom.y, 'ro', markersize=5, label='Point')
            
        # 2. 如果是多边形 (Polygon) -> 画蓝框 + 浅蓝填充
        elif geom_type == 'Polygon':
            x, y = geom.exterior.xy
            # 画轮廓
            ax.plot(x, y, color='#6699cc', alpha=0.7, linewidth=2, solid_capstyle='round', zorder=2)
            # 填充颜色 (用 fill 模拟)
            ax.fill(x, y, color='#6699cc', alpha=0.3)

        # 3. 如果是多部件多边形 (MultiPolygon) -> 稍微复杂点，遍历每个部件
        elif geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                x, y = poly.exterior.xy
                ax.plot(x, y, color='#6699cc', alpha=0.7, linewidth=2)
                ax.fill(x, y, color='#6699cc', alpha=0.3)

    # 设置坐标轴比例相等，防止地图变形 (这是 GIS 绘图的关键)
    ax.set_aspect('equal')
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 保存图片
    plt.savefig(output_path, dpi=150)
    # 关闭画布释放内存
    plt.close()
    
    print(f" -> 可视化图片已保存至: {output_path}")