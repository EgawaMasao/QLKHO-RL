"""
Demo: Lưu và Load Q-table cho Inventory Management
====================================================

Script này demo nhanh 2 chức năng:
1. Lưu model sau khi train
2. Load model đã lưu để tái sử dụng
"""

import numpy as np
import pickle
import os
from datetime import datetime

# Giả lập Q-table đã train (thực tế sẽ lấy từ notebook)
Q_demo = np.random.rand(41, 2) * -100  # 41 states x 2 actions

# Tham số demo
params_demo = {
    'alpha': 0.2,
    'gamma': 0.9,
    'epsilon': 0.1,
    'num_episodes': 1000,
    'episode_length': 1000,
    'O': 50.0,
    'h': 0.0274,
    'b': 20.0,
    'q': 6,
    'r': 3,
    'mu': 3.0,
    'sigma': 1.0
}

training_info_demo = {
    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'final_avg_cost': 2458.32,
    'best_episode_cost': 2341.12,
    'total_episodes': 1000
}


def save_demo_model():
    """Lưu model demo"""
    print("🔹 DEMO: Lưu model")
    print("-" * 50)
    
    model_data = {
        'Q_table': Q_demo,
        'params': params_demo,
        'training_info': training_info_demo,
        'states': np.arange(-20, 21),
        'actions': [0, 1],
        'min_IP': -20,
        'max_IP': 20
    }
    
    # Tạo thư mục nếu chưa có
    os.makedirs("../models", exist_ok=True)
    
    filename = "../models/q_table_demo.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(model_data, f)
    
    file_size = os.path.getsize(filename) / 1024  # KB
    print(f"✅ Đã lưu model vào: {filename}")
    print(f"   - File size: {file_size:.2f} KB")
    print(f"   - Q-table shape: {Q_demo.shape}")
    print(f"   - Timestamp: {training_info_demo['timestamp']}")
    print()


def load_demo_model():
    """Load model demo"""
    print("🔹 DEMO: Load model")
    print("-" * 50)
    
    filename = "../models/q_table_demo.pkl"
    
    if not os.path.exists(filename):
        print(f"File {filename} không tồn tại!")
        return None
    
    with open(filename, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f"Đã load model từ: {filename}")
    print(f"   - Q-table shape: {model_data['Q_table'].shape}")
    print(f"   - Training date: {model_data['training_info']['timestamp']}")
    print(f"   - Final avg cost: {model_data['training_info']['final_avg_cost']:.2f} €")
    print(f"   - Params: alpha={model_data['params']['alpha']}, "
          f"gamma={model_data['params']['gamma']}")
    print()
    
    # Kiểm tra Q-table có giống không
    if np.array_equal(model_data['Q_table'], Q_demo):
        print("Q-table khớp 100% với bản gốc!")
    else:
        print("Q-table khác với bản gốc (có thể đã train lại)")
    
    return model_data


def compare_models():
    """So sánh nhiều model versions"""
    print("DEMO: So sánh model versions")
    print("-" * 50)
    
    # Giả lập có 2 models
    versions = [
        {"name": "v1 (alpha=0.2)", "avg_cost": 2458.32},
        {"name": "v2 (alpha=0.5)", "avg_cost": 2401.18},
        {"name": "v3 (gamma=0.5)", "avg_cost": 2423.67},
    ]
    
    print("Bảng so sánh performance:\n")
    print(f"{'Model':<20} {'Avg Cost (€)':<15} {'Improvement':<15}")
    print("-" * 50)
    
    baseline = versions[0]['avg_cost']
    for v in versions:
        improvement = (baseline - v['avg_cost']) / baseline * 100
        print(f"{v['name']:<20} {v['avg_cost']:<15.2f} {improvement:>+.2f}%")
    
    best = min(versions, key=lambda x: x['avg_cost'])
    print(f"\nModel tốt nhất: {best['name']} với cost = {best['avg_cost']:.2f} €")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("  DEMO: Q-Learning Model Persistence")
    print("=" * 50)
    print()
    
    # Test 1: Save
    save_demo_model()
    
    # Test 2: Load
    loaded = load_demo_model()
    
    # Test 3: Compare
    compare_models()
    
    print("=" * 50)
    print(" Demo hoàn tất!")
    print("=" * 50)
    print()
    print(" Hướng dẫn chi tiết: xem file MODEL_USAGE.md")
