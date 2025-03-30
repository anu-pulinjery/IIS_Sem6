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
    def __init__(self,blno,txns,prev_bhash,miner_id):
        self.blckno=blno
        self.txns=txns
        self.prev_bhash=prev_bhash
        self.merkle_tree=merkletree(txns)
        self.nonce, self.blckhash=self.pow() 
        self.miner_id=miner_id

    def calculate_block_hash(self):
        if (self.blckno==0):
            return 0
        txt=f"{self.prev_bhash}{self.blckno}{self.merkle_tree.merkle_root}"
        return hashlib.sha3_256(txt.encode('utf-8')).hexdigest()
    
    def calculate_nonce(self,blckh,nonce):
        txt=f"{blckh}{nonce}"
        return hashlib.sha3_256(txt.encode('utf-8')).hexdigest()
    
    def pow(self):
        nonce=0
        blckh=(self.calculate_block_hash())
        while True:
            ch=str(self.calculate_nonce(blckh,nonce))
            if ch[-1]=="0":
                return nonce, blckh
            nonce=nonce+1
    
    def dict(self):
        return {"blckno":self.blckno,"blckhash":self.blckhash,"txns":self.txns,"merkleRoot":self.merkle_tree.merkle_root, "nonce":self.nonce, "miner_id":self.miner_id}
    
class blockChain:
    def __init__(self):
        self.accnts={}
        self.blocks=[]
        self.block_limit=4
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block=block(0,[],0, "A")
        self.blocks.append(genesis_block)

    def add_account(self,acc,balance):
        self.accnts[acc]=balance

    def process_transactions(self,txns,miners,com,bhsa):
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
            m=0
            miner_id=-1
            val=0
            for i in range(len(miners)):
                val=com[i]*(bhsa[i][len(self.blocks)])
                if val>m:
                    m=val
                    miner_id=miners[i]
            self.create_block(batch,miner_id)

    def create_block(self,txns,miner_id):
         prev_block_hash=self.blocks[-1].blckhash if self.blocks else "0"
         size=len(self.blocks)
         new_block=block(size,txns,prev_block_hash,miner_id)
         self.blocks.append(new_block)

    def display_blockchain(self):
        self.blocks=self.blocks[1:]
        for block in self.blocks:
            print(block.blckno)
            print(block.blckhash)
            print("[")
            for i in block.txns:
                print(i.to_list())
            print("]")
            print(block.merkle_tree.merkle_root)
            print(f"{block.nonce} {block.miner_id}")

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

num_miners=int(input())
miners=[]
com=[]
bhsa=[]
for _ in range(num_miners):
    j=input().split()
    miners.append(j[0])
    com.append(int(j[1]))
    a=[]
    for i in range(7):
        a.append(int(j[2+i]))
    bhsa.append(a)

# Process Transactions in Batches
blockchain.process_transactions(transactions,miners,com,bhsa)

# Display Output
blockchain.display_blockchain()