"""
Blockchain Implementation with Proof-of-Work
=============================================
Một implementation đầy đủ của blockchain với các tính năng:
- Block class với tất cả attributes cần thiết
- Blockchain class để quản lý chain
- Proof-of-Work (PoW) mining algorithm
- Chain validation để kiểm tra tính toàn vẹn
- Demo application với nhiều tính năng

"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Literal

# Định nghĩa các thuật toán hash được hỗ trợ
HashAlgorithm = Literal["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]


class Block:
    """
    Block class đại diện cho một block trong blockchain
    
    Attributes:
        index (int): Vị trí của block trong chain
        timestamp (float): Thời gian tạo block (Unix timestamp)
        data (Any): Dữ liệu được lưu trong block
        previous_hash (str): Hash của block trước đó
        nonce (int): Số dùng cho Proof-of-Work
        hash (str): Hash của block hiện tại
        hash_algorithm (str): Thuật toán hash được sử dụng
    """
    
    def __init__(self, index: int, timestamp: float, data: Any, previous_hash: str, 
                 nonce: int = 0, hash_algorithm: HashAlgorithm = "sha256"):
        """
        Khởi tạo một Block mới
        
        Args:
            index: Vị trí của block trong chain
            timestamp: Thời gian tạo block
            data: Dữ liệu cần lưu trữ
            previous_hash: Hash của block trước
            nonce: Giá trị nonce cho PoW (mặc định 0)
            hash_algorithm: Thuật toán hash (sha256, sha512, sha3-256, sha3-512, blake2b)
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash_algorithm = hash_algorithm
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Tính toán hash của block sử dụng thuật toán được chọn
        
        Hash được tính dựa trên tất cả các attributes của block:
        index, timestamp, data, previous_hash, và nonce
        
        Hỗ trợ các thuật toán:
        - SHA-256: Được Bitcoin sử dụng
        - SHA-512: Phiên bản mạnh hơn của SHA-2
        - SHA3-256: Thuật toán Keccak, được Ethereum sử dụng
        - SHA3-512: Phiên bản mạnh hơn của SHA-3
        - BLAKE2b: Nhanh hơn MD5, an toàn như SHA-3
        
        Returns:
            str: Hash của block dưới dạng hex string
        """
        # Kết hợp tất cả thông tin của block thành một string
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        # Tính hash theo thuật toán được chọn
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha512":
            return hashlib.sha512(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha3-256":
            return hashlib.sha3_256(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha3-512":
            return hashlib.sha3_512(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "blake2b":
            return hashlib.blake2b(block_string.encode()).hexdigest()
        else:
            # Fallback to SHA-256
            return hashlib.sha256(block_string.encode()).hexdigest()
    
    def __str__(self) -> str:
        """String representation của Block"""
        return f"Block #{self.index} [Hash: {self.hash[:16]}...]"
    
    def to_dict(self) -> Dict:
        """
        Chuyển block thành dictionary để dễ dàng hiển thị
        
        Returns:
            Dict: Dictionary chứa thông tin block
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "hash_algorithm": self.hash_algorithm
        }


class Blockchain:
    """
    Blockchain class quản lý toàn bộ chain
    
    Attributes:
        chain (List[Block]): Danh sách các blocks trong blockchain
        difficulty (int): Độ khó cho Proof-of-Work (số lượng số 0 đầu tiên)
        hash_algorithm (str): Thuật toán hash sử dụng cho toàn bộ chain
    """
    
    def __init__(self, difficulty: int = 4, hash_algorithm: HashAlgorithm = "sha256"):
        """
        Khởi tạo blockchain mới với genesis block
        
        Args:
            difficulty: Độ khó cho PoW (số lượng số 0 đầu hash, mặc định 4)
            hash_algorithm: Thuật toán hash (sha256, sha512, sha3-256, sha3-512, blake2b)
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.hash_algorithm = hash_algorithm
        # Tạo genesis block (block đầu tiên)
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """
        Tạo genesis block - block đầu tiên trong blockchain
        
        Genesis block có:
        - Index = 0
        - Previous hash = "0"
        - Data đặc biệt đánh dấu là genesis block
        
        Returns:
            Block: Genesis block đã được tạo và thêm vào chain
        """
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data="Genesis Block - The beginning of the blockchain",
            previous_hash="0",
            hash_algorithm=self.hash_algorithm
        )
        self.chain.append(genesis_block)
        print(f"✓ Genesis block created: {genesis_block.hash[:16]}...")
        print(f"  Hash Algorithm: {self.hash_algorithm.upper()}")
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """
        Lấy block cuối cùng trong chain
        
        Returns:
            Block: Block cuối cùng
        """
        return self.chain[-1]
    
    def add_block(self, data: Any) -> Block:
        """
        Thêm block mới vào blockchain (với mining)
        
        Process:
        1. Tạo block mới với data
        2. Mine block (Proof-of-Work)
        3. Thêm vào chain
        
        Args:
            data: Dữ liệu cần lưu trong block mới
            
        Returns:
            Block: Block mới đã được mine và thêm vào chain
        """
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            hash_algorithm=self.hash_algorithm
        )
        
        # Mine block với Proof-of-Work
        self.mine_block(new_block)
        
        # Thêm vào chain
        self.chain.append(new_block)
        return new_block
    
    def mine_block(self, block: Block) -> None:
        """
        Mine một block sử dụng Proof-of-Work algorithm
        
        PoW yêu cầu tìm một nonce sao cho hash của block bắt đầu
        với một số lượng số 0 nhất định (difficulty)
        
        Ví dụ: Với difficulty=4, hash phải bắt đầu với "0000"
        
        Args:
            block: Block cần mine
        """
        target = "0" * self.difficulty
        start_time = time.time()
        
        print(f"\n⛏️  Mining block #{block.index}...")
        print(f"   Target: {target}...")
        
        # Tìm nonce để hash thỏa mãn điều kiện
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
            
            # Hiển thị tiến trình mỗi 100,000 lần thử
            if block.nonce % 100000 == 0:
                print(f"   Trying nonce: {block.nonce:,} - Hash: {block.hash[:16]}...")
        
        elapsed_time = time.time() - start_time
        print(f"✓ Block mined!")
        print(f"   Nonce: {block.nonce:,}")
        print(f"   Hash: {block.hash}")
        print(f"   Time: {elapsed_time:.2f} seconds")
    
    def is_chain_valid(self) -> bool:
        """
        Kiểm tra tính hợp lệ của toàn bộ blockchain
        
        Validation checks:
        1. Hash của mỗi block phải đúng (tính lại và so sánh)
        2. Previous_hash phải trùng với hash của block trước
        3. Hash phải thỏa mãn difficulty (PoW)
        
        Returns:
            bool: True nếu chain hợp lệ, False nếu không
        """
        print("\n🔍 Validating blockchain...")
        
        # Bỏ qua genesis block, bắt đầu từ block 1
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check 1: Hash của block có đúng không?
            if current_block.hash != current_block.calculate_hash():
                print(f"✗ Block #{i}: Hash không hợp lệ!")
                print(f"   Expected: {current_block.calculate_hash()}")
                print(f"   Got: {current_block.hash}")
                return False
            
            # Check 2: Previous hash có khớp không?
            if current_block.previous_hash != previous_block.hash:
                print(f"✗ Block #{i}: Previous hash không khớp!")
                print(f"   Expected: {previous_block.hash}")
                print(f"   Got: {current_block.previous_hash}")
                return False
            
            # Check 3: Hash có thỏa mãn difficulty không?
            target = "0" * self.difficulty
            if not current_block.hash.startswith(target):
                print(f"✗ Block #{i}: Hash không thỏa mãn difficulty!")
                print(f"   Required: {target}...")
                print(f"   Got: {current_block.hash[:len(target)]}...")
                return False
            
            print(f"✓ Block #{i} is valid")
        
        print("✓ Blockchain is completely valid!")
        return True
    
    def get_chain_info(self) -> Dict:
        """
        Lấy thông tin tổng quan về blockchain
        
        Returns:
            Dict: Thông tin blockchain
        """
        return {
            "length": len(self.chain),
            "difficulty": self.difficulty,
            "hash_algorithm": self.hash_algorithm,
            "latest_block_hash": self.get_latest_block().hash,
            "genesis_block_hash": self.chain[0].hash
        }
    
    def print_chain(self) -> None:
        """In ra toàn bộ blockchain với format đẹp"""
        print("\n" + "="*70)
        print("BLOCKCHAIN OVERVIEW")
        print("="*70)
        
        info = self.get_chain_info()
        print(f"Chain Length: {info['length']} blocks")
        print(f"Difficulty: {info['difficulty']}")
        print(f"Hash Algorithm: {info['hash_algorithm'].upper()}")
        print(f"Genesis Block: {info['genesis_block_hash'][:16]}...")
        print(f"Latest Block: {info['latest_block_hash'][:16]}...")
        print("="*70)
        
        for block in self.chain:
            print(f"\n--- Block #{block.index} ---")
            print(f"Timestamp: {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Data: {block.data}")
            print(f"Previous Hash: {block.previous_hash[:16]}...")
            print(f"Nonce: {block.nonce:,}")
            print(f"Hash: {block.hash}")
        
        print("\n" + "="*70)


def demonstrate_tampering(blockchain: Blockchain) -> None:
    """
    Demo về việc blockchain chống lại tampering (giả mạo dữ liệu)
    
    Minh họa:
    1. Thay đổi data của một block giữa chain
    2. Validate chain để phát hiện giả mạo
    
    Args:
        blockchain: Blockchain để demo
    """
    print("\n" + "="*70)
    print("DEMO: TAMPERING DETECTION")
    print("="*70)
    
    if len(blockchain.chain) < 3:
        print("Need at least 3 blocks for this demo")
        return
    
    # Lưu dữ liệu gốc
    original_data = blockchain.chain[1].data
    original_hash = blockchain.chain[1].hash
    
    print(f"\n📝 Original Block #1 data: {original_data}")
    print(f"   Original hash: {original_hash[:16]}...")
    
    # Validation trước khi thay đổi
    print("\n--- Validating BEFORE tampering ---")
    is_valid_before = blockchain.is_chain_valid()
    
    # Giả mạo dữ liệu
    print("\n⚠️  TAMPERING: Changing data in Block #1...")
    blockchain.chain[1].data = "HACKED DATA - This has been modified!"
    print(f"   New data: {blockchain.chain[1].data}")
    print(f"   Hash remains: {blockchain.chain[1].hash[:16]}... (unchanged)")
    
    # Validation sau khi thay đổi
    print("\n--- Validating AFTER tampering ---")
    is_valid_after = blockchain.is_chain_valid()
    
    # Khôi phục dữ liệu gốc
    blockchain.chain[1].data = original_data
    blockchain.chain[1].hash = original_hash
    
    print("\n📊 Result:")
    print(f"   Valid before tampering: {is_valid_before}")
    print(f"   Valid after tampering: {is_valid_after}")
    print("\n💡 Conclusion: Blockchain successfully detected the tampering!")
    print("="*70)


def interactive_demo():
    """
    Interactive demo application với nhiều tính năng
    
    Cho phép user:
    - Chọn hash algorithm
    - Chọn difficulty level
    - Thêm blocks với data tùy chỉnh
    - Validate chain
    - Xem chain
    - Demo tampering detection
    """
    print("="*70)
    print("BLOCKCHAIN DEMO APPLICATION")
    print("="*70)
    
    # Chọn hash algorithm
    print("\nChọn thuật toán Hash:")
    print("1. SHA-256 (Bitcoin) - 256 bit, nhanh")
    print("2. SHA-512 - 512 bit, an toàn hơn")
    print("3. SHA3-256 (Keccak/Ethereum) - 256 bit, hiện đại")
    print("4. SHA3-512 - 512 bit, hiện đại nhất")
    print("5. BLAKE2b - Nhanh nhất, rất an toàn")
    
    hash_algorithms = {
        "1": "sha256",
        "2": "sha512", 
        "3": "sha3-256",
        "4": "sha3-512",
        "5": "blake2b"
    }
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-5): ").strip()
            if choice in hash_algorithms:
                hash_algorithm = hash_algorithms[choice]
                break
            print("Lựa chọn không hợp lệ!")
        except:
            print("Lựa chọn không hợp lệ!")
    
    # Chọn difficulty
    print("\nChọn độ khó (difficulty) cho Proof-of-Work:")
    print("1. Easy (difficulty = 2) - Nhanh, cho testing")
    print("2. Medium (difficulty = 3) - Cân bằng")
    print("3. Hard (difficulty = 4) - Mất thời gian hơn, an toàn hơn")
    print("4. Very Hard (difficulty = 5) - Rất chậm, production-ready")
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-4): ").strip()
            difficulty_map = {"1": 2, "2": 3, "3": 4, "4": 5}
            if choice in difficulty_map:
                difficulty = difficulty_map[choice]
                break
            print("Lựa chọn không hợp lệ!")
        except:
            print("Lựa chọn không hợp lệ!")
    
    # Khởi tạo blockchain
    print(f"\n🔗 Initializing blockchain...")
    print(f"   Hash Algorithm: {hash_algorithm.upper()}")
    print(f"   Difficulty: {difficulty}")
    blockchain = Blockchain(difficulty=difficulty, hash_algorithm=hash_algorithm)
    
    # Menu chính
    while True:
        print("\n" + "="*70)
        print("MENU")
        print("="*70)
        print("1. Thêm block mới vào blockchain")
        print("2. Hiển thị toàn bộ blockchain")
        print("3. Validate blockchain")
        print("4. Xem thông tin blockchain")
        print("5. Demo tampering detection")
        print("6. Thoát")
        
        choice = input("\nNhập lựa chọn (1-6): ").strip()
        
        if choice == "1":
            # Thêm block mới
            data = input("\nNhập dữ liệu cho block mới: ").strip()
            if data:
                blockchain.add_block(data)
                print(f"\n✓ Block đã được thêm vào blockchain!")
            else:
                print("Dữ liệu không được để trống!")
        
        elif choice == "2":
            # Hiển thị blockchain
            blockchain.print_chain()
        
        elif choice == "3":
            # Validate blockchain
            is_valid = blockchain.is_chain_valid()
            if is_valid:
                print("\n✓ Blockchain is VALID! ✓")
            else:
                print("\n✗ Blockchain is INVALID! ✗")
        
        elif choice == "4":
            # Thông tin blockchain
            info = blockchain.get_chain_info()
            print("\n" + "="*70)
            print("BLOCKCHAIN INFO")
            print("="*70)
            print(f"Total Blocks: {info['length']}")
            print(f"Difficulty: {info['difficulty']}")
            print(f"Genesis Block Hash: {info['genesis_block_hash']}")
            print(f"Latest Block Hash: {info['latest_block_hash']}")
            print("="*70)
        
        elif choice == "5":
            # Demo tampering
            if len(blockchain.chain) < 3:
                print("\n⚠️  Cần ít nhất 3 blocks để demo tampering.")
                print("   Hãy thêm thêm blocks trước!")
            else:
                demonstrate_tampering(blockchain)
        
        elif choice == "6":
            # Thoát
            print("\n👋 Cảm ơn bạn đã sử dụng Blockchain Demo!")
            print("="*70)
            break
        
        else:
            print("\n⚠️  Lựa chọn không hợp lệ!")


def quick_demo():
    """
    Quick demo tự động để test nhanh tất cả tính năng
    
    Demo sẽ:
    1. Tạo blockchain
    2. Thêm nhiều blocks
    3. Validate chain
    4. Demo tampering detection
    """
    print("="*70)
    print("QUICK AUTOMATIC DEMO")
    print("="*70)
    
    # Tạo blockchain với difficulty = 3 cho demo nhanh
    print("\n🔗 Creating blockchain với difficulty = 3...")
    blockchain = Blockchain(difficulty=3)
    
    # Thêm một số blocks
    print("\n📦 Adding blocks...")
    blockchain.add_block("Transaction 1: Alice sends 10 BTC to Bob")
    blockchain.add_block("Transaction 2: Bob sends 5 BTC to Charlie")
    blockchain.add_block("Transaction 3: Charlie sends 2 BTC to David")
    
    # Hiển thị blockchain
    blockchain.print_chain()
    
    # Validate
    blockchain.is_chain_valid()
    
    # Demo tampering
    demonstrate_tampering(blockchain)
    
    print("\n✓ Quick demo completed!")


if __name__ == "__main__":
    """
    Main entry point của chương trình
    
    Cho phép chọn giữa:
    1. Interactive demo - Tương tác đầy đủ
    2. Quick demo - Demo tự động nhanh
    """
    print("\n🔐 BLOCKCHAIN WITH PROOF-OF-WORK 🔐")
    print("\nChọn chế độ:")
    print("1. Interactive Demo (Recommended - Tương tác đầy đủ)")
    print("2. Quick Automatic Demo (Nhanh - Tự động)")
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-2): ").strip()
            if choice == "1":
                interactive_demo()
                break
            elif choice == "2":
                quick_demo()
                break
            else:
                print("Lựa chọn không hợp lệ!")
        except KeyboardInterrupt:
            print("\n\n👋 Thoát chương trình!")
            break
        except Exception as e:
            print(f"\n⚠️  Lỗi: {e}")
            break
