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

# Khởi tạo Flask app
app = Flask(__name__)
# Tạo secret key ngẫu nhiên để bảo mật session (16 bytes = 32 hex characters)
app.secret_key = secrets.token_hex(16)

# Dictionary để lưu trữ các blockchain instances
# Key: session_id (unique cho mỗi blockchain)
# Value: Blockchain object
blockchains = {}

# Thư mục để lưu trữ lịch sử các blockchain đã tạo
HISTORY_DIR = "blockchain_history"
# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)


@app.route('/')
def index():
    """
    Route cho trang chủ (landing page)
    Render file HTML template chính
    """
    return render_template('index.html')


@app.route('/create-blockchain', methods=['POST'])
def create_blockchain():
    """
    API endpoint để tạo blockchain mới
    
    Request JSON body:
        - difficulty (int): Độ khó cho mining (số lượng số 0 đầu hash)
        - hash_algorithm (str): Thuật toán hash ('sha256', 'sha512', 'sha3-256', 'sha3-512', 'blake2b')
    
    Returns:
        JSON response với thông tin blockchain mới được tạo
        - success (bool): Trạng thái thành công
        - session_id (str): ID unique để identify blockchain này
        - message (str): Thông báo
        - chain_info (dict): Thông tin về blockchain
    """
    try:
        # Parse JSON data từ request
        data = request.get_json()
        difficulty = int(data.get('difficulty', 3))  # Default difficulty = 3
        hash_algorithm = data.get('hash_algorithm', 'sha256')  # Default SHA-256
        
        # Tạo session ID unique (16 bytes = 32 hex chars) để identify blockchain này
        session_id = secrets.token_hex(8)
        
        # Khởi tạo Blockchain object mới với config đã chọn
        blockchain = Blockchain(difficulty=difficulty, hash_algorithm=hash_algorithm)
        
        # Lưu blockchain vào dictionary với session_id làm key
        blockchains[session_id] = blockchain
        
        # Trả về response JSON
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Blockchain created with {hash_algorithm.upper()}, difficulty {difficulty}',
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        # Nếu có lỗi, trả về error response với status code 400
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/add-block', methods=['POST'])
def add_block():
    """
    API endpoint để thêm block mới vào blockchain
    
    Request JSON body:
        - session_id (str): ID của blockchain cần thêm block
        - data (any): Dữ liệu cần lưu trong block (transaction, message, etc.)
    
    Returns:
        JSON response với thông tin block mới được mine
        - success (bool): Trạng thái thành công
        - block (dict): Thông tin block vừa được thêm
        - mining_time (float): Thời gian mining (giây)
        - chain_info (dict): Thông tin cập nhật về blockchain
    """
    try:
        # Parse JSON data
        data = request.get_json()
        session_id = data.get('session_id')
        block_data = data.get('data')
        
        # Kiểm tra blockchain có tồn tại không
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        # Lấy blockchain object
        blockchain = blockchains[session_id]
        
        # Đo thời gian mining để thống kê
        start_time = time.time()
        # Thêm block mới (sẽ tự động mining với PoW)
        new_block = blockchain.add_block(block_data)
        mining_time = time.time() - start_time
        
        # Trả về response với thông tin block vừa mine
        return jsonify({
            'success': True,
            'block': new_block.to_dict(),
            'mining_time': round(mining_time, 3),  # Làm tròn 3 chữ số thập phân
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/get-chain/<session_id>')
def get_chain(session_id):
    """
    API endpoint để lấy toàn bộ blockchain
    
    URL Parameters:
        - session_id (str): ID của blockchain cần xem
    
    Returns:
        JSON response với toàn bộ chain data
        - success (bool): Trạng thái thành công
        - chain (list): Danh sách tất cả blocks trong blockchain
        - chain_info (dict): Thông tin tổng quan về blockchain
    """
    try:
        # Kiểm tra blockchain có tồn tại không
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        # Lấy blockchain object
        blockchain = blockchains[session_id]
        
        # Convert tất cả blocks sang dictionary format để trả về JSON
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
    """
    API endpoint để validate (kiểm tra tính hợp lệ) của blockchain
    
    URL Parameters:
        - session_id (str): ID của blockchain cần validate
    
    Returns:
        JSON response với kết quả validation
        - success (bool): Trạng thái API call
        - is_valid (bool): Blockchain có hợp lệ hay không
        - chain_info (dict): Thông tin blockchain
        
    Validation checks:
        1. Hash của mỗi block phải đúng (recalculate và compare)
        2. Previous_hash phải match với hash của block trước
        3. Hash phải satisfy difficulty requirement (PoW)
    """
    try:
        # Kiểm tra blockchain có tồn tại không
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        # Gọi hàm validation từ Blockchain class
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
    """
    API endpoint để demo tampering (giả mạo) detection
    
    Request JSON body:
        - session_id (str): ID của blockchain
        - block_index (int): Index của block cần tamper
    
    Returns:
        JSON response với kết quả demo
        - success (bool): Trạng thái API call
        - original_data: Dữ liệu gốc của block
        - new_data: Dữ liệu sau khi tamper
        - tampered_detected (bool): Blockchain có phát hiện tampering hay không
        - message: Mô tả chi tiết
        
    Demo này cho thấy:
        - Khi data của một block bị thay đổi mà không recalculate hash
        - Blockchain sẽ phát hiện ra ngay lập tức khi validation
        - Đây là tính năng bảo mật quan trọng của blockchain
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        block_index = int(data.get('block_index'))
        
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        # Kiểm tra block index có hợp lệ không
        if block_index >= len(blockchain.chain):
            return jsonify({'success': False, 'error': 'Block index out of range'}), 400
        
        # Lưu data gốc để có thể show comparison
        original_data = blockchain.chain[block_index].data
        
        # Giả mạo data (KHÔNG tính lại hash - đây là điểm quan trọng!)
        # Trong thực tế, attacker sẽ thay đổi data nhưng không thể tính lại hash đúng
        # vì không biết nonce của block tiếp theo
        blockchain.chain[block_index].data = "⚠️ HACKED DATA - This block has been tampered!"
        
        # Validate để blockchain tự động phát hiện tampering
        is_valid = blockchain.is_chain_valid()
        
        # KHÔNG khôi phục data - để user thấy được blockchain đã bị tamper
        
        return jsonify({
            'success': True,
            'original_data': original_data,
            'new_data': blockchain.chain[block_index].data,
            'tampered_detected': not is_valid,  # True nếu phát hiện được tamper
            'message': f'Đã thay đổi dữ liệu Block #{block_index} từ "{original_data}" → "HACKED DATA". Blockchain đã phát hiện việc giả mạo!',
            'chain_info': blockchain.get_chain_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/save-blockchain', methods=['POST'])
def save_blockchain():
    """
    API endpoint để lưu blockchain vào file JSON (history)
    
    Request JSON body:
        - session_id (str): ID của blockchain cần save
        - name (str, optional): Tên cho blockchain (default: blockchain_YYYYMMDD_HHMMSS)
    
    Returns:
        JSON response với thông tin file đã save
        - success (bool): Trạng thái
        - message: Thông báo
        - filename: Đường dẫn file đã save
        
    File được save sẽ chứa:
        - Tên blockchain
        - Timestamp
        - Configuration (difficulty, hash algorithm)
        - Toàn bộ chain data
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        # Tạo tên mặc định với timestamp nếu không có name
        name = data.get('name', f"blockchain_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if session_id not in blockchains:
            return jsonify({'success': False, 'error': 'Blockchain not found'}), 404
        
        blockchain = blockchains[session_id]
        
        # Tạo data structure để save
        save_data = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'difficulty': blockchain.difficulty,
            'hash_algorithm': blockchain.hash_algorithm,
            'chain': [block.to_dict() for block in blockchain.chain]
        }
        
        # Save to JSON file trong HISTORY_DIR
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
    """
    API endpoint để lấy danh sách các blockchain đã save
    
    Returns:
        JSON response với danh sách history
        - success (bool): Trạng thái
        - history (list): Danh sách các blockchain đã save, mỗi item chứa:
            - filename: Tên file
            - name: Tên blockchain
            - timestamp: Thời gian save
            - difficulty: Độ khó
            - hash_algorithm: Thuật toán hash
            - blocks: Số lượng blocks
            
    History được sort theo timestamp giảm dần (mới nhất trước)
    """
    try:
        history_files = []
        
        # Kiểm tra thư mục history có tồn tại không
        if os.path.exists(HISTORY_DIR):
            # Duyệt qua tất cả files trong thư mục
            for filename in os.listdir(HISTORY_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(HISTORY_DIR, filename)
                    try:
                        # Đọc file JSON
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Thêm thông tin vào history list
                            history_files.append({
                                'filename': filename,
                                'name': data.get('name', filename),
                                'timestamp': data.get('timestamp', ''),
                                'difficulty': data.get('difficulty', 0),
                                'hash_algorithm': data.get('hash_algorithm', 'sha256'),
                                'blocks': len(data.get('chain', []))
                            })
                    except:
                        # Skip file nếu không đọc được
                        pass
        
        # Sort theo timestamp giảm dần (mới nhất lên đầu)
        history_files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'history': history_files
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/load-blockchain', methods=['POST'])
def load_blockchain():
    """
    API endpoint để load blockchain từ file history
    
    Request JSON body:
        - filename (str): Tên file cần load
    
    Returns:
        JSON response với blockchain đã load
        - success (bool): Trạng thái
        - session_id (str): Session ID mới cho blockchain đã load
        - message: Thông báo
        - chain_info: Thông tin blockchain
        
    Process:
        1. Đọc file JSON từ history
        2. Tạo session ID mới
        3. Recreate blockchain với config từ file
        4. Recreate tất cả blocks với data đã save
        5. Lưu vào blockchains dictionary
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        filepath = os.path.join(HISTORY_DIR, filename)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Load data từ JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Tạo session ID mới cho blockchain này
        session_id = secrets.token_hex(8)
        
        # Tạo blockchain mới với config từ file
        blockchain = Blockchain(
            difficulty=saved_data['difficulty'],
            hash_algorithm=saved_data.get('hash_algorithm', 'sha256')
        )
        
        # Xóa genesis block tự động được tạo
        blockchain.chain = []
        
        # Recreate tất cả blocks từ saved data
        for block_data in saved_data['chain']:
            # Tạo Block object với data đã save
            block = Block(
                index=block_data['index'],
                timestamp=block_data['timestamp'],
                data=block_data['data'],
                previous_hash=block_data['previous_hash'],
                nonce=block_data['nonce'],
                hash_algorithm=block_data.get('hash_algorithm', 'sha256')
            )
            # Set hash trực tiếp (không cần mine lại)
            block.hash = block_data['hash']
            # Thêm vào chain
            blockchain.chain.append(block)
        
        # Lưu blockchain vào dictionary
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
    """
    API endpoint để xóa một blockchain từ history
    
    Request JSON body:
        - filename (str): Tên file cần xóa
    
    Returns:
        JSON response với kết quả
        - success (bool): Trạng thái
        - message: Thông báo
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        filepath = os.path.join(HISTORY_DIR, filename)
        
        # Kiểm tra và xóa file
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
    """
    API endpoint để reset (xóa) blockchain hiện tại
    
    Request JSON body:
        - session_id (str): ID của blockchain cần reset
    
    Returns:
        JSON response với kết quả
        - success (bool): Trạng thái
        - message: Thông báo
        
    Xóa blockchain khỏi memory để user có thể tạo blockchain mới
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Xóa blockchain khỏi dictionary nếu tồn tại
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
# Routes này dùng để so sánh hiệu năng của các thuật toán hash khác nhau
# và test các tính năng như collision resistance
# ============================================================================

@app.route('/compare-algorithms')
def compare_algorithms():
    """
    API endpoint để so sánh hiệu năng các thuật toán hash
    
    Query Parameters:
        - difficulty (int, optional): Độ khó để test (default: 3)
    
    Returns:
        JSON response với kết quả so sánh
        - success (bool): Trạng thái
        - difficulty (int): Độ khó đã test
        - results (list): Kết quả của từng thuật toán (order gốc)
        - results_sorted (list): Kết quả đã sort theo mining_time
        - fastest: Thuật toán nhanh nhất
        - slowest: Thuật toán chậm nhất
        
    Test này sẽ:
        1. Tạo blockchain với mỗi thuật toán
        2. Mine một block với cùng data
        3. Đo thời gian mining
        4. So sánh kết quả
        
    Điều này giúp hiểu:
        - Thuật toán nào nhanh/chậm hơn
        - Hash length của mỗi thuật toán
        - Nonce cần thiết để mine (phụ thuộc vào thuật toán)
    """
    try:
        # Lấy difficulty từ query parameter
        difficulty = int(request.args.get('difficulty', 3))
        
        # Danh sách các thuật toán cần test
        algorithms = ["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]
        test_data = "Test Block - Comparing hash algorithms"
        
        results = []
        
        # Test từng thuật toán
        for algo in algorithms:
            # Tạo blockchain với thuật toán này
            blockchain = Blockchain(difficulty=difficulty, hash_algorithm=algo)
            
            # Mine một block và đo thời gian
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
                'hash_bits': len(new_block.hash) * 4,  # Mỗi hex char = 4 bits
                'hash': new_block.hash,
                'difficulty': difficulty
            })
        
        # Sort theo mining time để tìm nhanh/chậm nhất
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


def calculate_hash_similarity(hash1, hash2):
    """
    Tính độ giống nhau giữa 2 hash ở mức bit
    
    Args:
        hash1 (str): Hash thứ nhất (hex string)
        hash2 (str): Hash thứ hai (hex string)
    
    Returns:
        tuple: (similarity_percentage, changed_bits, total_bits)
        
    Giải thích:
        - Convert hex → binary để so sánh từng bit
        - Đếm số bits khác nhau
        - % giống nhau = (total_bits - changed_bits) / total_bits * 100
        
    Avalanche effect tốt:
        - ~50% bits thay đổi khi input thay đổi 1 ký tự
        - Similarity gần 50% = tốt nhất (random)
        - <40% hoặc >60% = có pattern (không tốt)
    """
    # Handle empty strings
    if not hash1 or not hash2:
        return 0, 0, 0
    
    # Convert hex to binary
    bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
    bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
    
    # Đảm bảo cùng độ dài
    max_len = max(len(bin1), len(bin2))
    bin1 = bin1.zfill(max_len)
    bin2 = bin2.zfill(max_len)
    
    # Đếm bits khác nhau
    changed_bits = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
    total_bits = len(bin1)
    
    # Tính % giống nhau (không phải % khác nhau)
    if total_bits == 0:
        return 0, 0, 0
    
    similarity = ((total_bits - changed_bits) / total_bits) * 100
    
    return round(similarity, 2), changed_bits, total_bits


def calculate_string_similarity(str1, str2):
    """
    Tính độ giống nhau giữa 2 strings (input)
    
    Args:
        str1 (str): String thứ nhất
        str2 (str): String thứ hai
    
    Returns:
        float: % giống nhau (0-100)
        
    Sử dụng Levenshtein distance:
        - Đếm số thao tác cần thiết để chuyển str1 → str2
        - Operations: insert, delete, replace
        - Similarity = (1 - distance/max_len) * 100
        
    Ví dụ:
        - "Hello" vs "Hello!" → ~91% giống (thêm 1 char)
        - "cat" vs "dog" → 0% giống (replace all)
    """
    # Handle empty strings
    if not str1 and not str2:
        return 100.0
    if not str1 or not str2:
        return 0.0
    
    # Levenshtein distance using dynamic programming
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],      # delete
                                  dp[i][j - 1],      # insert
                                  dp[i - 1][j - 1])  # replace
    
    distance = dp[m][n]
    max_len = max(m, n)
    
    # Tính % giống nhau
    if max_len == 0:
        return 100.0
    
    similarity = (1 - distance / max_len) * 100
    return round(similarity, 2)


def evaluate_avalanche_quality(similarity_percent):
    """
    Đánh giá chất lượng avalanche effect
    
    Args:
        similarity_percent (float): % giống nhau giữa 2 hash
    
    Returns:
        dict: {'quality': str, 'description': str}
        
    Tiêu chuẩn:
        - 45-55%: Excellent (ideal randomness)
        - 40-60%: Good (acceptable avalanche)
        - 30-70%: Fair (có pattern nhẹ)
        - <30% hoặc >70%: Poor (có vấn đề)
    """
    if 45 <= similarity_percent <= 55:
        return {
            'quality': 'Excellent',
            'description': 'Avalanche effect lý tưởng - ~50% bits thay đổi'
        }
    elif 40 <= similarity_percent <= 60:
        return {
            'quality': 'Good',
            'description': 'Avalanche effect tốt - đủ random'
        }
    elif 30 <= similarity_percent <= 70:
        return {
            'quality': 'Fair',
            'description': 'Avalanche effect chấp nhận được nhưng có pattern nhẹ'
        }
    else:
        return {
            'quality': 'Poor',
            'description': 'Avalanche effect yếu - có vấn đề về security'
        }


@app.route('/test-collision')
def test_collision():
    """
    API endpoint để test collision resistance với custom inputs
    
    Query Parameters (optional):
        - input1 (str): Text thứ nhất để hash
        - input2 (str): Text thứ hai để hash
    
    Returns:
        JSON response với kết quả test
        - success (bool): Trạng thái
        - results (list): Kết quả cho mỗi thuật toán với metrics chi tiết
        - input_similarity (float): % giống nhau giữa 2 inputs
        
    Test này demo "avalanche effect":
        - Hash 2 strings rất giống nhau
        - Chỉ khác 1 ký tự nhưng hash hoàn toàn khác nhau
        - Similarity ~50% (half bits changed = ideal)
        
    Metrics được tính:
        - Hash similarity: % bits giống nhau giữa 2 hash
        - Changed bits: Số bits thay đổi
        - Avalanche quality: Đánh giá chất lượng (Excellent/Good/Fair/Poor)
        - Input similarity: % giống nhau giữa 2 inputs
    """
    try:
        algorithms = ["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]
        
        # Get custom inputs from query parameters (nếu có)
        data1 = request.args.get('input1', 'Hello World')
        data2 = request.args.get('input2', 'Hello World!')
        
        print(f"\n🔍 DEBUG: Received inputs - input1='{data1}', input2='{data2}'")
        
        # Tính độ giống nhau giữa 2 inputs
        input_similarity = calculate_string_similarity(data1, data2)
        
        print(f"✓ Input similarity calculated: {input_similarity}%")
        
        results = []
        
        # Test từng thuật toán
        for algo in algorithms:
            print(f"\n⚙️  Processing algorithm: {algo}")
            blockchain = Blockchain(difficulty=1, hash_algorithm=algo)
            
            # Mine 2 blocks với data khác nhau
            block1 = blockchain.add_block(data1)
            block2 = blockchain.add_block(data2)
            
            print(f"   Block1 hash: {block1.hash[:16]}...")
            print(f"   Block2 hash: {block2.hash[:16]}...")
            
            # Tính similarity giữa 2 hash
            similarity, changed_bits, total_bits = calculate_hash_similarity(
                block1.hash, block2.hash
            )
            
            print(f"   Similarity: {similarity}%, Changed bits: {changed_bits}/{total_bits}")
            
            # Đánh giá avalanche quality
            avalanche = evaluate_avalanche_quality(similarity)
            
            results.append({
                'algorithm': algo.upper(),
                'data1': data1,
                'hash1': block1.hash,
                'data2': data2,
                'hash2': block2.hash,
                'similarity': similarity,
                'changed_bits': changed_bits,
                'total_bits': total_bits,
                'avalanche_quality': avalanche['quality'],
                'avalanche_description': avalanche['description']
            })
        
        print(f"\n✅ All algorithms processed successfully")
        
        return jsonify({
            'success': True,
            'input_similarity': input_similarity,
            'results': results
        })
    except Exception as e:
        print(f"\n❌ ERROR in test_collision: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/difficulty-comparison/<algorithm>')
def difficulty_comparison(algorithm):
    """
    API endpoint để so sánh mining time với các difficulty khác nhau
    
    URL Parameters:
        - algorithm (str): Thuật toán hash cần test
    
    Returns:
        JSON response với kết quả
        - success (bool): Trạng thái
        - algorithm (str): Thuật toán đã test
        - results (list): Kết quả cho mỗi difficulty level
        
    Test này cho thấy:
        - Difficulty càng cao → Mining time càng lâu (exponential)
        - Mối quan hệ giữa difficulty và thời gian mining
        - Nonce cần thiết tăng theo difficulty
        
    Giải thích:
        - Difficulty = 2: Hash phải bắt đầu với "00" (~256 tries)
        - Difficulty = 3: Hash phải bắt đầu với "000" (~4,096 tries)
        - Difficulty = 4: Hash phải bắt đầu với "0000" (~65,536 tries)
        - Difficulty = 5: Hash phải bắt đầu với "00000" (~1,048,576 tries)
        
    Mỗi tăng 1 difficulty → Tăng ~16x số lần thử (vì hex = base 16)
    """
    try:
        # Test với 4 difficulty levels
        difficulties = [2, 3, 4, 5]
        test_data = f"Testing {algorithm} with different difficulties"
        
        results = []
        
        # Test từng difficulty level
        for diff in difficulties:
            blockchain = Blockchain(difficulty=diff, hash_algorithm=algorithm)
            
            # Mine block và đo thời gian
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
    # Banner khi start server
    print("\n" + "="*70)
    print("🔗 BLOCKCHAIN WEB APPLICATION")
    print("="*70)
    print("\n🚀 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\n⚡ Press Ctrl+C to stop the server\n")
    
    # Start Flask development server
    # debug=True: Auto reload khi có thay đổi code, show error details
    # host='0.0.0.0': Listen trên tất cả network interfaces
    # port=5000: Port để run server
    app.run(debug=True, host='0.0.0.0', port=5000)
