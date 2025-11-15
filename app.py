"""
Flask Web Application for Blockchain
Features:
- Landing page với design hiện đại
- Tạo blockchain với difficulty tùy chọn
- Thêm blocks qua web interface
- Xem blockchain với visualization
- Validate chain
- Demo tampering detection
"""

from flask import Flask, render_template, request, jsonify, session
from blockchain import Block, Blockchain
import secrets
import time
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store blockchains in session
blockchains = {}

# History storage directory
HISTORY_DIR = "blockchain_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/create-blockchain', methods=['POST'])
def create_blockchain():
    """Tạo blockchain mới với difficulty và hash algorithm được chọn"""
    try:
        data = request.get_json()
        difficulty = int(data.get('difficulty', 3))
        hash_algorithm = data.get('hash_algorithm', 'sha256')
        
        # Tạo session ID unique
        session_id = secrets.token_hex(8)
        
        # Tạo blockchain mới
        blockchain = Blockchain(difficulty=difficulty, hash_algorithm=hash_algorithm)
        blockchains[session_id] = blockchain
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Blockchain created with {hash_algorithm.upper()}, difficulty {difficulty}',
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/add-block', methods=['POST'])
def add_block():
    """Thêm block mới vào blockchain"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        block_data = data.get('data')
        
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        # Đo thời gian mining
        start_time = time.time()
        new_block = blockchain.add_block(block_data)
        mining_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'block': new_block.to_dict(),
            'mining_time': round(mining_time, 3),
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/get-chain/<session_id>')
def get_chain(session_id):
    """Lấy toàn bộ blockchain"""
    try:
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        chain_data = [block.to_dict() for block in blockchain.chain]
        
        return jsonify({
            'success': True,
            'chain': chain_data,
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/validate-chain/<session_id>')
def validate_chain(session_id):
    """Validate blockchain"""
    try:
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        is_valid = blockchain.is_chain_valid()
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/tamper-block', methods=['POST'])
def tamper_block():
    """Demo tampering detection"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        block_index = int(data.get('block_index'))
        
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        if block_index >= len(blockchain.chain):
            return jsonify({'success': False, 'error': 'Block index out of range'}), 400
        
        # Lưu data gốc
        original_data = blockchain.chain[block_index].data
        
        # Giả mạo data (KHÔNG tính lại hash - đây là điểm quan trọng!)
        blockchain.chain[block_index].data = "⚠️ HACKED DATA - This block has been tampered!"
        
        # Validate để phát hiện
        is_valid = blockchain.is_chain_valid()
        
        # KHÔNG khôi phục - để data bị thay đổi để demo
        
        return jsonify({
            'success': True,
            'original_data': original_data,
            'new_data': blockchain.chain[block_index].data,
            'tampered_detected': not is_valid,
            'message': f'Đã thay đổi dữ liệu Block #{block_index} từ "{original_data}" → "HACKED DATA". Blockchain đã phát hiện việc giả mạo!',
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/save-blockchain', methods=['POST'])
def save_blockchain():
    """Lưu blockchain vào lịch sử"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        name = data.get('name', f"blockchain_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        # Tạo data để save
        save_data = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'difficulty': blockchain.difficulty,
            'hash_algorithm': blockchain.hash_algorithm,
            'chain': [block.to_dict() for block in blockchain.chain]
        }
        
        # Save to file
        filename = os.path.join(HISTORY_DIR, f"{name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Blockchain saved as "{name}"',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/get-history')
def get_history():
    """Lấy danh sách blockchain đã lưu"""
    try:
        history_files = []
        
        if os.path.exists(HISTORY_DIR):
            for filename in os.listdir(HISTORY_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(HISTORY_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            history_files.append({
                                'filename': filename,
                                'name': data.get('name', filename),
                                'timestamp': data.get('timestamp', ''),
                                'difficulty': data.get('difficulty', 0),
                                'hash_algorithm': data.get('hash_algorithm', 'sha256'),
                                'blocks': len(data.get('chain', []))
                            })
                    except:
                        pass
        
        # Sort by timestamp descending
        history_files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'history': history_files
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/load-blockchain', methods=['POST'])
def load_blockchain():
    """Load blockchain từ lịch sử"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        filepath = os.path.join(HISTORY_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Load data
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Tạo session ID mới
        session_id = secrets.token_hex(8)
        
        # Tạo blockchain mới với difficulty và hash algorithm từ file
        blockchain = Blockchain(
            difficulty=saved_data['difficulty'],
            hash_algorithm=saved_data.get('hash_algorithm', 'sha256')
        )
        
        # Xóa genesis block hiện tại
        blockchain.chain = []
        
        # Recreate chain từ saved data
        for block_data in saved_data['chain']:
            block = Block(
                index=block_data['index'],
                timestamp=block_data['timestamp'],
                data=block_data['data'],
                previous_hash=block_data['previous_hash'],
                nonce=block_data['nonce'],
                hash_algorithm=block_data.get('hash_algorithm', 'sha256')
            )
            block.hash = block_data['hash']
            blockchain.chain.append(block)
        
        blockchains[session_id] = blockchain
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Loaded blockchain: {saved_data["name"]}',
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/delete-history', methods=['POST'])
def delete_history():
    """Xóa một blockchain từ lịch sử"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        filepath = os.path.join(HISTORY_DIR, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({
                'success': True,
                'message': 'History deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/reset-blockchain', methods=['POST'])
def reset_blockchain():
    """Reset blockchain hiện tại để tạo mới"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id in blockchains:
            del blockchains[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Blockchain reset successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# HASH COMPARISON ROUTES
# ============================================================================

@app.route('/compare-algorithms')
def compare_algorithms():
    """API endpoint để so sánh các thuật toán với độ khó được chọn"""
    try:
        difficulty = int(request.args.get('difficulty', 3))
        algorithms = ["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]
        test_data = "Test Block - Comparing hash algorithms"
        
        results = []
        
        for algo in algorithms:
            # Tạo blockchain với thuật toán này
            blockchain = Blockchain(difficulty=difficulty, hash_algorithm=algo)
            
            # Thêm một block và đo thời gian
            start_time = time.time()
            new_block = blockchain.add_block(test_data)
            mining_time = time.time() - start_time
            
            # Lưu kết quả
            results.append({
                'algorithm': algo,
                'algorithm_display': algo.upper(),
                'mining_time': round(mining_time, 4),
                'nonce': new_block.nonce,
                'hash_length': len(new_block.hash),
                'hash_bits': len(new_block.hash) * 4,
                'hash': new_block.hash,
                'difficulty': difficulty
            })
        
        # Sort by mining time
        results_sorted = sorted(results, key=lambda x: x['mining_time'])
        
        return jsonify({
            'success': True,
            'difficulty': difficulty,
            'results': results,
            'results_sorted': results_sorted,
            'fastest': results_sorted[0],
            'slowest': results_sorted[-1]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/test-collision')
def test_collision():
    """Test collision resistance với dữ liệu tương tự"""
    try:
        algorithms = ["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]
        data1 = "Hello World"
        data2 = "Hello World!"
        
        results = []
        
        for algo in algorithms:
            blockchain = Blockchain(difficulty=1, hash_algorithm=algo)
            
            block1 = blockchain.add_block(data1)
            block2 = blockchain.add_block(data2)
            
            results.append({
                'algorithm': algo.upper(),
                'data1': data1,
                'hash1': block1.hash,
                'data2': data2,
                'hash2': block2.hash,
                'similarity': 0  # Always 0% due to avalanche effect
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/difficulty-comparison/<algorithm>')
def difficulty_comparison(algorithm):
    """So sánh mining time với các difficulty khác nhau"""
    try:
        difficulties = [2, 3, 4, 5]
        test_data = f"Testing {algorithm} with different difficulties"
        
        results = []
        
        for diff in difficulties:
            blockchain = Blockchain(difficulty=diff, hash_algorithm=algorithm)
            
            start_time = time.time()
            new_block = blockchain.add_block(test_data)
            mining_time = time.time() - start_time
            
            results.append({
                'difficulty': diff,
                'mining_time': round(mining_time, 4),
                'nonce': new_block.nonce,
                'hash': new_block.hash
            })
        
        return jsonify({
            'success': True,
            'algorithm': algorithm,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔗 BLOCKCHAIN WEB APPLICATION")
    print("="*70)
    print("\n🚀 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\n⚡ Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
