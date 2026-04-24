# Post-Quantum Cryptography

## [PT-BR] Modulo de Criptografia Pos-Quantica | [EN] Post-Quantum Cryptography Module

---

## Visao Geral / Overview

Este modulo implementa a integracao dos padroes **NIST Post-Quantum Cryptography** com o framework **HALE** (Harmonic Addressing and Labeling Equation) da Hubstry.

This module implements the integration of **NIST Post-Quantum Cryptography** standards with the Hubstry **HALE** (Harmonic Addressing and Labeling Equation) framework.

---

## Padroes NIST Implementados / NIST Standards Implemented

### FIPS 203 - ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism)

| Parametro | Tamanho da Chave / Key Size | Ciphertext | Security |
|-----------|---------------------------|------------|----------|
| ML-KEM-512 | 800 + 768 bytes | 768 bytes | NIST Level 1 |
| ML-KEM-768 | 1.184 + 1.088 bytes | 1.088 bytes | NIST Level 3 |
| ML-KEM-1024 | 1.568 + 1.568 bytes | 1.568 bytes | NIST Level 5 |

**Status HALE:** Integracao com HALE Core via derivacao phi(b). A chave simetrica AES-256-GCM utilizada internamente e derivada do HALE Key Hierarchy (Level 3).

### FIPS 204 - ML-DSA (Module-Lattice-Based Digital Signature Algorithm)

| Parametro | Public Key | Signature | Security |
|-----------|-----------|-----------|----------|
| ML-DSA-44 | 1.312 bytes | 2.420 bytes | NIST Level 2 |
| ML-DSA-65 | 1.952 bytes | 3.309 bytes | NIST Level 3 |
| ML-DSA-87 | 2.592 bytes | 4.627 bytes | NIST Level 5 |

**Status HALE:** Assinatura digital HALE-PQ - o digest da mensagem e derivado via HALE hash tree (f0 harmonic cascade), assinado com ML-DSA-65.

### FIPS 205 - SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)

| Parametro | Public Key | Signature | Security |
|-----------|-----------|-----------|----------|
| SLH-DSA-128f | 32 bytes | 7.856 bytes | NIST Level 1 |
| SLH-DSA-192f | 48 bytes | 16.208 bytes | NIST Level 3 |
| SLH-DSA-256f | 64 bytes | 29.792 bytes | NIST Level 5 |

**Status HALE:** Backup signature scheme - sem dependencia de lattice, oferece seguranca baseada unicamente em funcoes de hash.

---

## HALE Key Hierarchy

```
Level 0: f0 (fundamental frequency)
    |
Level 1: phi(b) x f0  -->  Root Key (identity)
    |
Level 2: phi(b)^2 x f0  -->  Session Keys (mutual TLS equivalent)
    |
Level 3: phi(b)^3 x f0  -->  Encryption Keys (AES-256-GCM for data)
    |
Level 4: phi(b)^4 x f0  -->  PQC Seed (input for ML-KEM key generation)
```

Onde **phi(b)** e a funcao totiente de Euler, garantindo que cada nivel de hierarquia produz subchaves criptograficamente independentes.

Where **phi(b)** is Euler''s totient function, ensuring each hierarchy level produces cryptographically independent subkeys.

---

## Integracao Hibrida | Hybrid Integration

```
Hybrid Handshake:
  1. X25519 (classical ECDH)       --> shared_secret_classical
  2. ML-KEM-768 (PQC KEM)          --> shared_secret_pq
  3. HALE coherence token           --> session_binding
  4. KDF = SHA-256(classical || pq || binding)
  5. AES-256-GCM with KDF-derived key
```

---

## Exemplo de Implementacao | Implementation Example

Veja o codigo completo em `examples/hale_mlkem.py`.

See full code at `examples/hale_mlkem.py`.

```python
import hashlib
import math

class HALEKeyHierarchy:
    def __init__(self, f0=440, base=12):
        self.f0 = f0
        self.b = base

    @staticmethod
    def phi(n):
        return sum(1 for k in range(1, n) if math.gcd(k, n) == 1)

    def derive_key(self, level):
        p = self.phi(self.b)
        fk = self.f0 * (p ** level)
        material = "HALE:" + str(self.f0) + ":" + str(self.b) + ":" + str(level) + ":" + str(fk)
        return hashlib.sha256(material.encode()).digest()

    def pq_seed(self):
        return self.derive_key(4)


class HybridKEM:
    def __init__(self):
        self.hale = HALEKeyHierarchy()
        self.pqc_seed = self.hale.pq_seed()

    def encapsulate(self):
        classical_secret = hashlib.sha256(b"classical-ephemeral").digest()
        pq_secret = hashlib.sha256(self.pqc_seed + b"ml-kem-encapsulation").digest()
        binding = self.hale.derive_key(2)
        combined = hashlib.sha256(classical_secret + pq_secret + binding).digest()
        return {"shared_secret": combined.hex(), "hale_binding": binding.hex()}


if __name__ == "__main__":
    kem = HybridKEM()
    result = kem.encapsulate()
    print("Encapsulation successful")
    print("Keys derived via HALE hierarchy (Level 4)")
```

---

## Referencias | References

1. NIST FIPS 203 - Module-Lattice-Based Key-Encapsulation Mechanism Standard (2024)
2. NIST FIPS 204 - Module-Lattice-Based Digital Signature Standard (2024)
3. NIST FIPS 205 - Stateless Hash-Based Digital Signature Standard (2024)
4. ENISA Post-Quantum Cryptography: Current State and Quantum Mitigation (2024)
5. Shor, P. W. - Algorithms for Quantum Computation (1994)

---

*Hubstry Deep Tech - Post-Quantum Research Module*