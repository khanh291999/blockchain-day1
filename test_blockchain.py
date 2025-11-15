"""
Unit Tests for Blockchain Implementation
=========================================
Test suite để kiểm tra tất cả tính năng của blockchain

Run tests:
    python test_blockchain.py
"""

import unittest
import time
from blockchain import Block, Blockchain


class TestBlock(unittest.TestCase):
    """Test cases cho Block class"""
    
    def setUp(self):
        """Setup cho mỗi test"""
        self.block = Block(
            index=1,
            timestamp=time.time(),
            data="Test Data",
            previous_hash="0000abcd",
            nonce=0
        )
    
    def test_block_creation(self):
        """Test tạo block thành công"""
        self.assertEqual(self.block.index, 1)
        self.assertEqual(self.block.data, "Test Data")
        self.assertEqual(self.block.previous_hash, "0000abcd")
        self.assertIsNotNone(self.block.hash)
    
    def test_calculate_hash(self):
        """Test hash calculation"""
        hash1 = self.block.calculate_hash()
        hash2 = self.block.calculate_hash()
        self.assertEqual(hash1, hash2, "Hash should be deterministic")
    
    def test_hash_changes_with_data(self):
        """Test hash thay đổi khi data thay đổi"""
        original_hash = self.block.hash
        self.block.data = "Modified Data"
        new_hash = self.block.calculate_hash()
        self.assertNotEqual(original_hash, new_hash)
    
    def test_to_dict(self):
        """Test chuyển block sang dictionary"""
        block_dict = self.block.to_dict()
        self.assertIn('index', block_dict)
        self.assertIn('timestamp', block_dict)
        self.assertIn('data', block_dict)
        self.assertIn('hash', block_dict)


class TestBlockchain(unittest.TestCase):
    """Test cases cho Blockchain class"""
    
    def setUp(self):
        """Setup cho mỗi test"""
        self.blockchain = Blockchain(difficulty=2)
    
    def test_genesis_block_creation(self):
        """Test genesis block được tạo tự động"""
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].previous_hash, "0")
    
    def test_add_block(self):
        """Test thêm block mới"""
        initial_length = len(self.blockchain.chain)
        self.blockchain.add_block("Test Transaction")
        self.assertEqual(len(self.blockchain.chain), initial_length + 1)
    
    def test_chain_linking(self):
        """Test các blocks được liên kết đúng"""
        self.blockchain.add_block("Block 1")
        self.blockchain.add_block("Block 2")
        
        for i in range(1, len(self.blockchain.chain)):
            current = self.blockchain.chain[i]
            previous = self.blockchain.chain[i-1]
            self.assertEqual(current.previous_hash, previous.hash)
    
    def test_proof_of_work(self):
        """Test Proof-of-Work hoạt động đúng"""
        self.blockchain.add_block("PoW Test")
        latest_block = self.blockchain.get_latest_block()
        target = "0" * self.blockchain.difficulty
        self.assertTrue(latest_block.hash.startswith(target))
    
    def test_chain_validation_valid_chain(self):
        """Test validation với chain hợp lệ"""
        self.blockchain.add_block("Block 1")
        self.blockchain.add_block("Block 2")
        self.assertTrue(self.blockchain.is_chain_valid())
    
    def test_chain_validation_tampered_data(self):
        """Test validation phát hiện data bị thay đổi"""
        self.blockchain.add_block("Original Data")
        # Giả mạo dữ liệu
        self.blockchain.chain[1].data = "Tampered Data"
        self.assertFalse(self.blockchain.is_chain_valid())
    
    def test_chain_validation_tampered_hash(self):
        """Test validation phát hiện hash bị thay đổi"""
        self.blockchain.add_block("Block 1")
        self.blockchain.add_block("Block 2")
        # Giả mạo hash
        self.blockchain.chain[1].hash = "fake_hash"
        self.assertFalse(self.blockchain.is_chain_valid())
    
    def test_get_latest_block(self):
        """Test lấy block cuối cùng"""
        self.blockchain.add_block("Latest Block")
        latest = self.blockchain.get_latest_block()
        self.assertEqual(latest.data, "Latest Block")
    
    def test_chain_info(self):
        """Test lấy thông tin blockchain"""
        self.blockchain.add_block("Block 1")
        info = self.blockchain.get_chain_info()
        self.assertEqual(info['length'], 2)
        self.assertEqual(info['difficulty'], 2)


class TestMining(unittest.TestCase):
    """Test cases cho mining functionality"""
    
    def test_mining_increases_nonce(self):
        """Test mining tăng nonce"""
        blockchain = Blockchain(difficulty=2)
        blockchain.add_block("Test Block")
        latest = blockchain.get_latest_block()
        self.assertGreater(latest.nonce, 0)
    
    def test_mining_produces_valid_hash(self):
        """Test hash sau mining thỏa mãn difficulty"""
        blockchain = Blockchain(difficulty=3)
        blockchain.add_block("Test Block")
        latest = blockchain.get_latest_block()
        self.assertTrue(latest.hash.startswith("000"))


def run_tests():
    """Chạy tất cả tests và hiển thị kết quả"""
    print("="*70)
    print("RUNNING BLOCKCHAIN UNIT TESTS")
    print("="*70)
    
    # Tạo test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Thêm tất cả test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBlock))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchain))
    suite.addTests(loader.loadTestsFromTestCase(TestMining))
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Hiển thị summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED! ✓")
    else:
        print("\n✗ SOME TESTS FAILED ✗")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
