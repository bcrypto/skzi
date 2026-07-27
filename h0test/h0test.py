#******************************************************************************
# \file h0test.py
# \brief Implementation of the statistical test suite defined in MI10127.12.03
# \created 2026.07.14
# \version 2026.07.20
# \license Public domain
# \ref https://apmi.bsu.by/resources/met
# \usage h0test.py {1Mb|10Mb} path/to/file[s]1 path/to/file[s]2 ...
#******************************************************************************

import sys, os
from math import exp, sqrt, log, comb, floor
from collections import Counter
from itertools import groupby
from scipy.stats import chi2, norm, poisson, binom
from scipy.fft import fft
from numpy import abs
from glob import glob

#******************************************************************************
# Критерии (статистические тесты)
#
# [in] seq -- обрабатываемая последовательность в виде (0,1)-строки
# [in] параметры теста (если имеются)
# [out] P-значение
#******************************************************************************

# Критерий многомерной дискретной равномерности 
# по непересекающимся отрезкам (МДРН)
def critMdrn(seq, L):
  assert(0 < L and len(seq) >= max(50, 10 * 2 ** L))

  freqs = Counter()
  for t in range(0, len(seq) - L + 1, L):
    freqs[int(seq[t : t + L], 2)] += 1

  S = 0.0
  mu = len(seq) // L / 2 ** L
  for v in range(2 ** L):
    S += (freqs[v] - mu) ** 2
  S /= mu

  return 1.0 - chi2.cdf(S, 2 ** L - 1)

# Критерий многомерной дискретной равномерности 
# по пересекающимся отрезкам (МДРП)
def critMdrp(seq, L):
  assert(1 < L and len(seq) >= 20 * 2 ** L)

  freqs = Counter()
  for t in range(len(seq) - L + 1):
    freqs[int(seq[t : t + L], 2)] += 1
  for t in range(len(seq) - L + 1, len(seq)):
    freqs[int(seq[t:] + seq[: L - len(seq) + t], 2)] += 1

  S = 0.0
  mu = len(seq) / 2 ** L
  for v in range(2 ** L):
    S += (freqs[v] - mu) ** 2
  S /= mu

  L1 = L - 1
  freqs1 = Counter()
  for t in range(len(seq) - L1 + 1):
    freqs1[int(seq[t : t + L1], 2)] += 1
  for t in range(len(seq) - L1 + 1, len(seq)):
    freqs1[int(seq[t:] + seq[: L1 - len(seq) + t], 2)] += 1

  S1 = 0.0
  mu1 = len(seq) / 2 ** L1
  for v in range(2 ** L1):
    S1 += (freqs1[v] - mu1) ** 2
  S1 /= mu1

  return 1.0 - chi2.cdf(S - S1, 2 ** L - 2 ** L1)

# Критерий "пустых ящиков" (КПЯ)
def critEmptyBox(seq, L):
  assert(0 < L and L < len(seq))

  freqs = Counter()
  m = len(seq) // L
  for t in range(m):
    freqs[int(seq[t * L : t * L + L], 2)] += 1
    
  S = 0
  for v in range(2 ** L):
    if freqs[v] > 1:
      S += freqs[v] - 1

  lmbda = m / 2 ** L
  assert(lmbda < 5)
  if lmbda < 1 / 32:
    mu = m ** 2 / 2 / 2 ** L
    pv = 1.0 - poisson.cdf(S, mu)
  else:
    mu0 = S + 2 ** L - m
    mu = 2 ** L * exp(-lmbda)
    sigma = sqrt(mu * (1 - (1 + lmbda) * exp(-lmbda)))
    pv = norm.cdf(-(mu0 - mu) / sigma)

  return pv

# Критерий серий (КС)
def critRuns(seq):
  assert(79 <= len(seq))

  freqs0, freqs1 = Counter(), Counter()
  for key, group in groupby(seq):
    length = len(list(group))
    if key == '0':
      freqs0[length] += 1
    else:
      freqs1[length] += 1

  S, k = 0.0, 0
  while True:
    mu = (len(seq) - (k + 1) + 3) / 2 ** (k + 3)
    if mu < 5:
      break
    k += 1
    S += ((freqs0[k] - mu) ** 2 + (freqs1[k] - mu) ** 2) / mu

  return 1.0 - chi2.cdf(S, 2 * k - 2)

# Критерий длинных серий (КДС)
def critLongRuns(seq, L):
  len_bounds = {8: 427, 128: 12464, 512: 50688, 1000: 100000, 10000: 1490000}
  intervals = {
    8: [range(0, 2), range(2, 3), range(3, 4), range(4, 9)],
    128: [range(0, 5), range(5, 6), range(6, 7), range(7, 8), range(8, 9), 
      range(9,129)],
    512: [range(0, 7), range(7, 8), range(8, 9), range(9, 10), range(10, 11), 
      range(11, 513)],
    1000: [range(0, 8), range(8, 9), range(9, 10), range(10, 11), 
       range(11, 12), range(12, 10001)],
    10000: [range(0, 11), range(11, 12), range(12, 13), range(13, 14), 
       range(14, 15), range(15, 16), range(16, 100001)],
  }
  probs = {
    8: [0.21484375, 0.3671875, 0.23046875, 0.1875],
    128: [0.1174035788, 0.2429559593, 0.2493634832, 0.1751770603, 0.1027010713,
      0.1123988471],
    512: [0.1299334833, 0.2361223453, 0.2418343719, 0.1729754256, 0.1032697631,
      0.1158646108],
    1000: [0.1388551909, 0.2369038167, 0.2387912400, 0.1700180792, 
      0.1014361440, 0.1139955292],
    10000: [0.0866323111, 0.2082006484, 0.2484185819, 0.1939127867, 
      0.1214584851, 0.0680110893, 0.0733660975]
  }
  assert(L in len_bounds and len_bounds[L] <= len(seq))

  m = len(seq) // L
  freqs = Counter()
  for t in range(m):
    max_len = len(max(seq[t * L : t * L + L].split('0')))
    for i in range(len(intervals[L])):
      if max_len in intervals[L][i]:
        freqs[i] += 1

  S = 0.0
  for i in range(len(intervals[L])):
    mu = m * probs[L][i]
    S += (freqs[i] - mu) ** 2 / mu

  return 1.0 - chi2.cdf(S, len(intervals[L]) - 1)

# Критерий аппроксимации энтропии (КАЭ)
def critApEntr(seq, L):
  assert(1 < L and L < len(seq))

  freqs = Counter()
  for t in range(len(seq) - L + 1):
    freqs[int(seq[t : t + L], 2)] += 1

  F = 0.0
  for v in range(2 ** L):
    if (freqs[v]):
      pi = freqs[v] / (len(seq) + 1 - L)
      F -= pi * log(pi)

  L1 = L - 1
  freqs1 = Counter()
  for t in range(len(seq) - L1 + 1):
    freqs1[int(seq[t : t + L1], 2)] += 1

  F1 = 0.0
  for v in range(2 ** L1):
    if (freqs1[v]):
      pi1 = freqs1[v] / (len(seq) + 1 - L1)
      F1 -= pi1 * log(pi1)

  S = 2 * len(seq) * abs(log(2.0) - F + F1)

  return 1.0 - chi2.cdf(S, 2 ** L - 2 ** L1)

# Критерий скалярного произведения (КСКП)
def critScalar(seq, m, K):
  assert(m in range(2, 9) and K in range(2, 12) and m * K < len(seq))

  L = m * K
  M = len(seq) // L
  freqs = Counter()
  for t in range(M):
    subseq1 = seq[t * L : t * L + m]
    max_product = 0
    for i in range(1, K):
      subseqi = seq[t * L + m * i : t * L + m * i + m]
      product = sum(a == '1' and b == '1' for a, b in zip(subseq1, subseqi))
      if product > max_product:
        max_product = product
    freqs[max_product] += 1

  q0 = 1 / 2 ** m * (1 + 2 / 2 ** K) ** m
  S = (freqs[0] - M * q0) ** 2 / (M * q0)
  for k in range(1, m + 1):
    qk = 0.0
    for l in range(m + 1):
      p1 = binom.cdf(k, l, 0.5) ** (K - 1)
      p2 = binom.cdf(k - 1, l, 0.5) ** (K - 1)
      qk += comb(m, l) * (p1 - p2)
    qk /= 2 ** m
    S += (freqs[k] - M * qk) ** 2 / (M * qk)

  return 1.0 - chi2.cdf(S, m)

# Спектральный критерий на основе быстрого преобразования Фурье (СК-БПФ)
def critSpectr(seq):
  assert(len(seq) >= 400)

  spectr = fft([2 * int(char) - 1 for char in seq])
  density = abs(spectr[: len(seq) // 2])

  h = sqrt(len(seq) * log(20.0))
  S = sum(1 for d in density if d < h)
  p = 0.95
  mu = len(seq) * p / 2
  sigma = sqrt(len(seq) * p * (1 - p) / 3.79)

  return 2 * (1.0 - norm.cdf(abs((S - mu) / sigma)))

#******************************************************************************
# Батареи
#
# [in] pvs -- P-значения
# [in] дополнительные параметры
# [out] агрегированное P-значение
#******************************************************************************

# Батарея Бернулли
def batBer(pvs, alpha):
  assert(1.0 / len(pvs) <= alpha and alpha < 1.0)

  S = sum(1 for pv in pvs if pv >= alpha)
  sigma = sqrt(alpha * (1.0 - alpha) / len(pvs))
  return 1.0 - norm.cdf(-(S / len(pvs) - (1 - alpha))/ sigma)

# Батарея Chi2
def batChi2(pvs, k):
  assert(10 <= k and k * 10 <= len(pvs))

  freqs = Counter()
  for pv in pvs:
    freqs[min(floor(pv * k), k - 1)] += 1

  S = 0.0
  for i in range(k):
    S += (freqs[i] - len(pvs) / k) ** 2 / (len(pvs) / k)

  return 1.0 - chi2.cdf(S, k - 1)

#******************************************************************************
# Тестирование одной последовательностей (ТОП)
#
# [in] seq -- последовательность
# [out] словарь P-значений двух батарей
#
# remark Для завершения тестирования следует передать выходной словарь в 
# функцию testPortrait() в качестве портрета.
#******************************************************************************

def testSingle(seq):
  if len(seq) == 2 ** 23:
    m, alpha, k, b = 104, 0.05, 10, 0
  elif len(seq) == 10 * 2 ** 23:
    m, alpha, k, b = 200, 0.05, 10, 1
  else:
    assert(True)

  n = len(seq) // m
  pvs = {}
  for i in range(m):
    subseq = seq[i * n : i * n + n]
    pvs.setdefault("mdrn", []).append(critMdrn(subseq, 9 + b * 2))
    pvs.setdefault("mdrp", []).append(critMdrp(subseq, 11 + b * 3))
    pvs.setdefault("emptybox", []).append(critEmptyBox(subseq, 18 + b * 4))
    pvs.setdefault("runs", []).append(critRuns(subseq))
    pvs.setdefault("longruns", []).append(critLongRuns(subseq, 128 + b * 872))
    pvs.setdefault("apentr", []).append(critApEntr(subseq, 9 + b * 3))
    pvs.setdefault("scalar", []).append(critScalar(subseq, 4, 10))
    pvs.setdefault("spectr", []).append(critSpectr(subseq))
    if i % 4 == 0:
      print(".", end="", flush=True)
  print("")

  for crit in pvs:
    pvs[crit] = [batBer(pvs[crit], alpha), batChi2(pvs[crit], k)]

  return pvs

#******************************************************************************
# Печать словаря P-значений
# 
# remark Ключ словаря -- имя теста, значение -- список P-значений теста.
# remark Заголовки столбцов с P-значениями можно настроить с помощью функции
# headers. Она принимает номер столбца (нумерация от 0) и возвращает строку 
# заголовка. По умолчанию, headers = lambda i: str(i + 1).
#******************************************************************************

def printPvs(pvs, headers=None):
  h0 = "criterion"
  h0_len = len(h0)
  m = len(next(iter(pvs.values())))
  for crit in pvs:
    assert(len(pvs[crit]) == m)
    h0_len = max(h0_len, len(crit))

  print(f"  | {h0:<{h0_len}} |", end="")
  for i in range(m):
    if headers:
      hi = headers(i)
    else:
      hi = str(i + 1)
    print(f" {hi:<8} |", end="") 
  print("")

  print(f"  | {'-' * h0_len} |", end="")
  for i in range(m):
    print(f" {'-' * 8} |", end="") 
  print("")

  for crit in pvs:
    print(f"  | {crit:<{h0_len}} |", end="")
    for i in range(m):
      print(f" {pvs[crit][i]:.6f} |", end="") 
    print("")

#******************************************************************************
# Тестирование нескольких последовательностей (ТНП)
#
# [in] portrait -- словарь P-значений (статистический портрет)
# [out] признак успеха
#
# remark Словарь portrait должен быть получен объединением словарей, которые
# возвращает функция testSingle(seq_i), где seq_i -- i-ая последовательность.
#******************************************************************************

def testPortrait(portrait, verbose=False):
  beta, gamma = 0.0001, 0.01

  M = len(next(iter(portrait.values())))
  assert(M >= 2 and M % 2 == 0)
  M /= 2

  nus = {}
  min_nu = 1.0
  for crit in portrait:
    assert(len(portrait[crit]) == 2 * M)
    nu1 = sum(pv >= beta for pv in portrait[crit][0::2]) / M
    nu2 = sum(pv >= beta for pv in portrait[crit][1::2]) / M
    min_nu = min(min_nu, nu1, nu2)
    nus[crit] = [nu1, nu2]

  if M == 1:
    success = min_nu > 0.0
  else:
    delta0 = max(0.0, 1.0 - gamma - 3.0 * sqrt(gamma * (1 - gamma) / M))
    delta1 = min(1.0, 1 - gamma + 3.0 * sqrt(gamma * (1 - gamma) / M))
    success = delta0 <= min_nu and min_nu <= delta1

  if verbose:
    print("Portrait:")
    printPvs(portrait, lambda i: f"seq{i // 2 + 1}-{i % 2 + 1}")
    print("Success rate:")
    printPvs(nus, lambda i: "1 (Bern)" if i % 2 == 0 else "2 (Chi2)")

  return success

#******************************************************************************
# Main
#
# usage:
#   h0test {1Mb|10Mb} path/to/the/file[s]1 path/to/the/file[s]2 ...
#
# remark Биты в байте файла прочитываются от старшего (первый) к младшему. 
# Изменение порядка:
#    seq = "".join(f"{byte:08b}"[::-1] for byte in f.read())
#******************************************************************************

def usage():
  print("Usage: h0test {1Mb|10Mb} path/to/file[s]1 path/to/file[s]2 ...")
  return -1

def main():
  if len(sys.argv) < 3:
    return usage()
  if sys.argv[1] == "1Mb":
    nb = 2 ** 20
  elif sys.argv[1] == "10Mb":
    nb = 10 * 2 ** 20
  else:
    return usage()

  portrait, count = {}, 0
  print("Processing sequences:")
  for i in range(2, len(sys.argv)): 
    for filename in glob(sys.argv[i], recursive=True):
      if os.path.getsize(filename) < nb:
        continue
      with open(filename, "rb") as file:
        part = 0
        while True:
          block = file.read(nb)
          if len(block) < nb:
            break
          count += 1
          part += 1
          print(f"* seq{count}: {filename}#{part}", end="")
          seq = "".join(f"{byte:08b}" for byte in block)
          pvs = testSingle(seq)
          if portrait:
            for crit in portrait:
              portrait[crit] += pvs[crit]
          else:
            portrait = pvs

  if not portrait:
    print("  none")
    return -1

  print("")
  if not testPortrait(portrait, True):
    print("H0: rejected")
    return 1
  print("H0: accepted")
  return 0

if __name__ == "__main__":
  main()
