#!/usr/bin/env python3
"""
分析 vLLM benchmark sweep 实验结果
用法: python3 analyze_results.py
"""
import json
import glob
import os
from pathlib import Path

RESULT_DIR = '/root/autodl-tmp/results/sweep_awq'


def load_results(pattern):
    """加载匹配的结果文件"""
    results = []
    for f in sorted(glob.glob(os.path.join(RESULT_DIR, pattern))):
        try:
            with open(f) as fp:
                d = json.load(fp)
            d['_filename'] = os.path.basename(f)
            results.append(d)
        except Exception as e:
            print(f"⚠️ 读取 {f} 失败: {e}")
    return results


def fmt(v, decimals=1):
    """格式化数字，None 显示 -"""
    if v is None or v == 0:
        return '-'
    return f"{v:.{decimals}f}"


def print_table_A(results):
    """实验组 A：固定 conc=32，扫 rate"""
    print("\n" + "=" * 120)
    print("📊 实验组 A: 固定 max-concurrency=32, 扫描 request-rate")
    print("=" * 120)
    
    header = f"{'Rate':>8} {'Duration(s)':>12} {'TTFT_P50':>10} {'TTFT_P99':>10} {'TPOT_P50':>10} {'TPOT_P99':>10} {'Out_TPS':>10} {'Total_TPS':>10} {'Peak_Conc':>10}"
    print(header)
    print("-" * 120)
    
    rows = []
    for d in results:
        rate = d.get('request_rate')
        # 安全处理 inf 的多种表示
        if rate is None or rate == 'inf' or (isinstance(rate, float) and rate == float('inf')):
            rate_str = 'inf'
            rate_num = float('inf')
        else:
            rate_num = float(rate)
            rate_str = str(int(rate_num)) if rate_num == int(rate_num) else str(rate_num)
        
        rows.append({
            'rate': rate_str,
            'rate_num': rate_num,
            'duration': d.get('duration', 0),
            'ttft_p50': d.get('median_ttft_ms', 0),
            'ttft_p99': d.get('p99_ttft_ms', 0),
            'tpot_p50': d.get('median_tpot_ms', 0),
            'tpot_p99': d.get('p99_tpot_ms', 0),
            'out_tps': d.get('output_throughput', 0),
            'total_tps': d.get('total_token_throughput', 0),
            'peak_conc': d.get('max_concurrent_requests', 0),
        })
    
    rows.sort(key=lambda x: x['rate_num'])
    
    for r in rows:
        print(f"{r['rate']:>8} {fmt(r['duration'], 1):>12} "
              f"{fmt(r['ttft_p50']):>10} {fmt(r['ttft_p99']):>10} "
              f"{fmt(r['tpot_p50'], 2):>10} {fmt(r['tpot_p99'], 2):>10} "
              f"{fmt(r['out_tps']):>10} {fmt(r['total_tps']):>10} "
              f"{fmt(r['peak_conc'], 0):>10}")
    
    return rows


def print_table_B(results):
    """实验组 B：固定 rate=inf，扫 concurrency"""
    print("\n" + "=" * 120)
    print("📊 实验组 B: 固定 request-rate=inf, 扫描 max-concurrency")
    print("=" * 120)
    
    header = f"{'Conc':>8} {'Duration(s)':>12} {'TTFT_P50':>10} {'TTFT_P99':>10} {'TPOT_P50':>10} {'TPOT_P99':>10} {'Out_TPS':>10} {'Total_TPS':>10} {'Peak_Conc':>10}"
    print(header)
    print("-" * 120)
    
    rows = []
    for d in results:
        conc = d.get('max_concurrency', 0)
        rows.append({
            'conc': conc,
            'duration': d.get('duration', 0),
            'ttft_p50': d.get('median_ttft_ms', 0),
            'ttft_p99': d.get('p99_ttft_ms', 0),
            'tpot_p50': d.get('median_tpot_ms', 0),
            'tpot_p99': d.get('p99_tpot_ms', 0),
            'out_tps': d.get('output_throughput', 0),
            'total_tps': d.get('total_token_throughput', 0),
            'peak_conc': d.get('max_concurrent_requests', 0),
        })
    
    rows.sort(key=lambda x: x['conc'])
    
    for r in rows:
        print(f"{r['conc']:>8} {fmt(r['duration'], 1):>12} "
              f"{fmt(r['ttft_p50']):>10} {fmt(r['ttft_p99']):>10} "
              f"{fmt(r['tpot_p50'], 2):>10} {fmt(r['tpot_p99'], 2):>10} "
              f"{fmt(r['out_tps']):>10} {fmt(r['total_tps']):>10} "
              f"{fmt(r['peak_conc'], 0):>10}")
    
    return rows


def analyze_throughput_saturation(rows_b):
    """分析吞吐饱和点"""
    print("\n" + "=" * 120)
    print("🎯 吞吐饱和分析（实验组 B）")
    print("=" * 120)
    
    if len(rows_b) < 2:
        print("  数据不足")
        return
    
    print(f"{'Conc':>8} {'Total_TPS':>12} {'相对 conc=1 提升':>20} {'相对上一档提升':>20}")
    print("-" * 70)
    base = rows_b[0]['total_tps'] or 1
    prev = base
    for r in rows_b:
        speedup_base = r['total_tps'] / base if base else 0
        speedup_prev = (r['total_tps'] / prev - 1) * 100 if prev else 0
        print(f"{r['conc']:>8} {r['total_tps']:>12.1f} {speedup_base:>18.2f}× {speedup_prev:>18.1f}%")
        prev = r['total_tps'] or prev
    
    # 找饱和点（相对上一档提升 < 10%）
    print("\n💡 饱和点判断:")
    for i in range(1, len(rows_b)):
        prev_tps = rows_b[i-1]['total_tps']
        curr_tps = rows_b[i]['total_tps']
        if prev_tps > 0 and (curr_tps / prev_tps - 1) < 0.10:
            print(f"   → 吞吐在 conc={rows_b[i-1]['conc']} 附近开始饱和（再加并发提升 <10%）")
            break


def analyze_slo(rows_a, ttft_p99_limit=400, tpot_p99_limit=50):
    """分析 SLO 满足情况"""
    print("\n" + "=" * 120)
    print(f"🎯 SLO 分析（TTFT_P99 < {ttft_p99_limit}ms 且 TPOT_P99 < {tpot_p99_limit}ms）")
    print("=" * 120)
    
    print(f"{'Rate':>8} {'TTFT_P99':>10} {'TPOT_P99':>10} {'Total_TPS':>12} {'达标?':>8} {'Goodput':>10}")
    print("-" * 70)
    
    best_goodput = 0
    best_rate = None
    for r in rows_a:
        ttft_ok = r['ttft_p99'] < ttft_p99_limit
        tpot_ok = r['tpot_p99'] < tpot_p99_limit
        passed = ttft_ok and tpot_ok
        goodput = r['total_tps'] if passed else 0
        if goodput > best_goodput:
            best_goodput = goodput
            best_rate = r['rate']
        
        mark = '✓' if passed else '✗'
        print(f"{r['rate']:>8} {fmt(r['ttft_p99']):>10} {fmt(r['tpot_p99'], 2):>10} "
              f"{fmt(r['total_tps']):>12} {mark:>8} {fmt(goodput):>10}")
    
    if best_rate:
        print(f"\n💡 在该 SLO 下最佳 rate = {best_rate}, Goodput = {best_goodput:.1f} tok/s")
    else:
        print(f"\n⚠️  没有任何 rate 满足这个 SLO，可能要放宽阈值或优化系统")


def analyze_tpot_limit(rows_b):
    """分析单请求 TPOT 极限"""
    print("\n" + "=" * 120)
    print("🎯 单请求 TPOT 物理极限分析（实验组 B, conc=1）")
    print("=" * 120)
    
    conc1 = next((r for r in rows_b if r['conc'] == 1), None)
    if not conc1:
        print("  没有 conc=1 的数据")
        return
    
    tpot_p50 = conc1['tpot_p50']
    # 理论值: Qwen2.5-7B BF16 ≈ 15GB / 3090 带宽 936GB/s
    theory = 15.0 / 936 * 1000  # ms
    efficiency = theory / tpot_p50 * 100 if tpot_p50 else 0
    
    print(f"  实测 TPOT P50 (conc=1):  {tpot_p50:.2f} ms")
    print(f"  理论下限 (带宽极限):     {theory:.2f} ms")
    print(f"  带宽利用率 MBU:          {efficiency:.1f}%")
    print(f"  优化空间:                {(tpot_p50 - theory):.2f} ms ({(1 - theory/tpot_p50)*100:.0f}%)")
    
    if efficiency > 80:
        print(f"  💡 已逼近带宽极限，纯软件优化空间有限，建议上量化（INT4 可降到约 {theory/2:.1f} ms）")
    elif efficiency > 60:
        print(f"  💡 接近带宽极限，调度优化空间约 20%，量化可以进一步翻倍")
    else:
        print(f"  ⚠️  带宽利用率偏低，可能有调度问题或 kernel 未优化")


def main():
    if not os.path.exists(RESULT_DIR):
        print(f"❌ 结果目录不存在: {RESULT_DIR}")
        return
    
    print(f"📂 读取目录: {RESULT_DIR}")
    print(f"📄 发现 {len(glob.glob(os.path.join(RESULT_DIR, '*.json')))} 个结果文件\n")
    
    # 加载实验组 A 和 B
    results_a = load_results('expA_*.json')
    results_b = load_results('expB_*.json')
    
    print(f"   实验组 A: {len(results_a)} 个结果")
    print(f"   实验组 B: {len(results_b)} 个结果")
    
    # 打印表格
    rows_a = print_table_A(results_a) if results_a else []
    rows_b = print_table_B(results_b) if results_b else []
    
    # 深度分析
    if rows_b:
        analyze_throughput_saturation(rows_b)
        analyze_tpot_limit(rows_b)
    
    if rows_a:
        # 不同 SLO 标准
        analyze_slo(rows_a, ttft_p99_limit=300, tpot_p99_limit=40)  # 严格 SLO（chatbot）
        analyze_slo(rows_a, ttft_p99_limit=500, tpot_p99_limit=60)  # 宽松 SLO（普通服务）
    
    print("\n" + "=" * 120)
    print("✅ 分析完成")
    print("=" * 120)


if __name__ == '__main__':
    main()