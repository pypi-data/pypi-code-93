import time

from noid import pynoid

acc = pynoid.mint(template='zeeeek')
print(acc)
accessions = list()
for i in range(500):
    acc = pynoid.mint(template='zddddddk', n=i)
    accessions.append(acc)
print(accessions)

# print(pynoid.validate(acc))
# acc = pynoid.mint(template='reeeeeek')
# print(acc)
# acc = pynoid.mint(template='reeeeeek')
# print(acc)
# accessions = list()
# duplicate = 0
# digits = 4
# start = time.time()
# while True:
#     print(f"#accessions: {len(accessions):,}", end='')
#     acc = pynoid.mint(template='z'+'e' * digits + 'k')
#     if len(accessions) > 99999:
#     # if len(accessions) >= len(pynoid.XDIGIT) ** digits:
#         stop = time.time()
#         break
#     accessions.append(acc)
#     print("\r", end='')
# print()
# print(accessions[:100])
# print(len(accessions))
# print(len(set(accessions)))
# print(f"purity: {round(len(set(accessions))/len(accessions), 6)}")
# print(f"duration: {round(stop - start, 4)}s")
