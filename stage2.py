import hashlib

class transaction:
    def __init__(self,fracc,toacc,amt,incentive):
        self.fro=fracc
        self.to=toacc
        self.amt=amt
        self.incentive=incentive

    def to_list(self):
        return [self.fro,self.to,self.amt,self.incentive]
    
    def hash_transaction(self):
        txn=f"{self.fro}{self.incentive}{self.to}{self.amt}"
        return hashlib.sha3_256(txn.encode('utf-8')).hexdigest()

class merkletree:
    def __init__(self,txns):
        self.txns=txns
        self.merkle_root=self.construct_merkle_tree()

    def construct_merkle_tree(self):
        hashes=[txn.hash_transaction() for txn in self.txns]
        while len(hashes)>1:
            new_hashes = []
            for i in range(0, len(hashes) - 1, 2):
                new_hashes.append(hashlib.sha3_256((hashes[i] + hashes[i+1]).encode('utf-8')).hexdigest())
            if len(hashes) % 2 == 1:
                new_hashes.append(hashes[-1])  # Do not duplicate the last node, append as is
            hashes = new_hashes
        return hashes[0] if hashes else "0"
    
class block:
    def __init__(self,blno,txns,prev_bhash):
        self.blckno=blno
        self.txns=txns
        self.prev_bhash=prev_bhash
        self.merkle_tree=merkletree(txns)
        self.blckhash=self.calculate_block_hash()

    def calculate_block_hash(self):
        if (self.blckno==0):
            return 0
        txt=f"{self.prev_bhash}{self.blckno}{self.merkle_tree.merkle_root}"
        return hashlib.sha3_256(txt.encode('utf-8')).hexdigest()
    
    def dict(self):
        return {"blckno":self.blckno,"blckhash":self.blckhash,"txns":self.txns,"merkleRoot":self.merkle_tree.merkle_root}
    
class blockChain:
    def __init__(self):
        self.accnts={}
        self.blocks=[]
        self.block_limit=3
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block=block(0,[],0)
        self.blocks.append(genesis_block)

    def add_account(self,acc,balance):
        self.accnts[acc]=balance

    def process_transactions(self,txns):
        a=[]
        txns.sort(key=lambda txn: (-txn[3], txn[1]))
        for txn in txns:
            sender, receiver, amount, incentive = txn
            if sender in self.accnts and self.accnts[sender] >= amount and receiver in self.accnts:
                self.accnts[sender] -= amount
                self.accnts[receiver] += amount
                a.append(transaction(sender, receiver, amount, incentive))
        for i in range(0,len(a),self.block_limit):
            batch=a[i:i+self.block_limit]
            self.create_block(batch)

    def create_block(self,txns):
         prev_block_hash=self.blocks[-1].blckhash if self.blocks else "0"
         size=len(self.blocks)
         new_block=block(size,txns,prev_block_hash)
         self.blocks.append(new_block)

    def display_blockchain(self):
        self.blocks=self.blocks[1:]
        for block in self.blocks:
            print(block.blckno)
            print(block.blckhash)
            print("[")
            for txn in block.txns:
                print(f"{txn.to_list()},")
            print("]")
            print(block.merkle_tree.merkle_root)


# Input Handling
print("enter input")
num_acc = int(input())
blockchain = blockChain()

for _ in range(num_acc):
    acc, bal = input().split()
    blockchain.add_account(acc, int(bal))

num_txn = int(input())
transactions=[]
for _ in range(num_txn):
    sender, receiver, amount, incentive = input().split()
    transactions.append([sender, receiver, int(amount), int(incentive)])

# Process Transactions in Batches
blockchain.process_transactions(transactions)

# Display Output
blockchain.display_blockchain()   