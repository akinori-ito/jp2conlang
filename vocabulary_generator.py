import random
import re
from collections import defaultdict, Counter

class VocabularyGenerator:
    def __init__(self, n=3):
        self.n = n
        self.model = defaultdict(Counter)
        self.start_sequences = []

    def _clean_text(self, text):
        """テキストからアルファベット以外を除去して小文字化する"""
        return re.sub(r'[^a-z\s]', '', text.lower())

    def train_from_string(self, text):
        """文字列から学習する"""
        clean_text = self._clean_text(text)
        words = clean_text.split()
        self._build_model(words)

    def train_from_file(self, file_path):
        """テキストファイルから学習する"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.train_from_string(text)
            print(f"Successfully trained from: {file_path}")
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")

    def _build_model(self, words):
        """単語リストからn-gramモデルを構築する内部メソッド"""
        for word in words:
            if len(word) < self.n:
                continue
            
            self.start_sequences.append(word[:self.n-1])
            
            for i in range(len(word) - self.n + 1):
                ngram = word[i:i+self.n]
                context = ngram[:self.n-1]
                target = ngram[self.n-1]
                self.model[context][target] += 1

    def generate_word(self, length):
        """指定された長さの単語を生成する"""
        if not self.model:
            return "none"

        # 開始シーケンスをランダムに選択
        current = random.choice(self.start_sequences)
        res = list(current)

        # 指定の長さに達するまで文字を追加
        while len(res) < length:
            context = "".join(res[-(self.n-1):])
            choices = self.model.get(context)

            if not choices:
                # 続きがない場合は新しい開始シーケンスから繋げる（擬似的なBack-off）
                res.extend(list(random.choice(self.start_sequences)))
                continue

            next_char = random.choices(
                list(choices.keys()), 
                weights=list(choices.values())
            )[0]
            res.append(next_char)

        return "".join(res)[:length]

# --- 使い方の例 ---
if __name__ == "__main__":
    gen = VocabularyGenerator(n=3)
    
    # 1. 文字列から学習する場合
    #gen.train_from_string("The quick brown fox jumps over the lazy dog.")
    
    # 2. ファイルから学習する場合（ファイルがある場合のみコメントアウト解除）
    gen.train_from_file("genesis.txt")

    print("--- 生成テスト ---")
    for _ in range(20):
        print(gen.generate_word(random.randint(4, 8)))