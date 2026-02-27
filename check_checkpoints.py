import tensorflow as tf
import os

checkpoint_folders = [
    'checkpoints_220',
    'checkpoints_dqn_comparison123',
    'checkpoints_dqn_comparison256',
    'checkpoints_dqn_comparison3primary',
    'checkpoints_dqn_comparison512',
    'checkpoints_dqn_comparison42',
    'checkpointDQN',
    'CheckpointDQN2',
    'checkpointDQN_trained',
    'checkpointDQN_A2Cstyle',
    'checkpointDQN_wandb'
]

base_path = r'c:\Study\NCKH\QLKHO-RL'

print("="*70)
print("🔍 CHECKING ALL CHECKPOINT FOLDERS")
print("="*70)

for folder in checkpoint_folders:
    full_path = os.path.join(base_path, folder)
    if not os.path.exists(full_path):
        continue
    
    latest = tf.train.latest_checkpoint(full_path)
    if not latest:
        continue
    
    print(f"\n{'='*70}")
    print(f"📁 {folder}")
    print(f"{'='*70}")
    
    try:
        reader = tf.train.load_checkpoint(latest)
        shapes = reader.get_variable_to_shape_map()
        
        # Check key indicators
        has_gn = any('gn' in k.lower() or 'group_norm' in k.lower() for k in shapes.keys())
        has_q_values = any('q_value' in k.lower() for k in shapes.keys())
        has_out = any('/out/' in k for k in shapes.keys())
        has_policy = any('policy' in k.lower() for k in shapes.keys())
        
        # Try to find hidden size
        hidden_size = None
        for k, shape in shapes.items():
            if len(shape) == 2 and ('dense1' in k.lower() or 'layer1' in k.lower()) and 'kernel' in k.lower():
                hidden_size = shape[1]
                break
        
        # Model type detection
        model_type = "Unknown"
        if has_policy:
            model_type = "A2C"
        elif has_q_values or has_out:
            model_type = "DQN"
        
        print(f"🎯 Model Type: {model_type}")
        print(f"📏 Hidden Size: {hidden_size}")
        print(f"🧬 Has GroupNorm: {has_gn}")
        print(f"🎲 Has q_values: {has_q_values}")
        print(f"🎯 Has out layer: {has_out}")
        
        # Show relevant variables (non-optimizer, non-target)
        print(f"\n📋 Key Variables:")
        count = 0
        for k in sorted(shapes.keys()):
            if 'optimizer' not in k.lower() and 'target' not in k.lower() and 'save' not in k.lower():
                if count < 10:
                    print(f"   • {k}: {shapes[k]}")
                    count += 1
        
        # Check if matches our DQNAgentRDX
        if model_type == "DQN" and hidden_size == 32 and not has_gn:
            print("\n🎉 ✅ THIS MATCHES DQNAgentRDX(hidden_size=32, no GroupNorm)!")
        elif model_type == "DQN" and hidden_size != 32:
            print(f"\n⚠️  DQN but wrong hidden_size ({hidden_size} vs 32)")
        elif model_type == "DQN" and has_gn:
            print(f"\n⚠️  DQN but has GroupNorm (architecture mismatch)")
            
    except Exception as e:
        print(f"❌ Error reading checkpoint: {e}")

print(f"\n{'='*70}")
print("✅ SCAN COMPLETE")
print(f"{'='*70}")
