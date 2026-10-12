# Q4: simple vector DB with cosine similarity written by hand (no numpy / no library)
#
# cosine similarity = (a . b) / (|a| * |b|)

import math
import json


def dot(a, b):
    result = 0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result


def magnitude(a):
    return math.sqrt(dot(a, a))


def cosine_similarity(a, b):
    return dot(a, b) / (magnitude(a) * magnitude(b))


class VectorDB:
    def __init__(self, file="vectors.json"):
        self.file = file
        self.data = []          # list of {"id":..., "vector":..., "text":...}
        self.load()

    def add(self, id, vector, text=""):
        self.data.append({"id": id, "vector": vector, "text": text})
        self.save()

    def search(self, query_vector, top_k=3):
        results = []
        for item in self.data:
            score = cosine_similarity(query_vector, item["vector"])
            results.append((score, item))

        # highest score first
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with open(self.file) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []


if __name__ == "__main__":
    db = VectorDB()
    db.add("1", [1, 0, 0], "apple")
    db.add("2", [0.9, 0.1, 0], "apple juice")
    db.add("3", [0, 1, 0], "car")

    for score, item in db.search([1, 0.1, 0]):
        print(round(score, 3), item["text"])
