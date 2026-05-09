# MnMCP - Minecraft and MiniWorld Cross-Platform CrossPlay
Archived, view the new repository: [MnMCP](https://github.com/StarsailsClover/MnMCP)

---

## Project Introduction
MnMCP is a cross-platform interconnection project between Minecraft and MiniWorld. It allows players of Minecraft Java Edition and Chinese mainland MiniWorld official server players to play together in the same world.

### Core Features
- ✅ Minecraft Java Protocol Support
- ✅ MiniWorld China Server Protocol Support (iLink/mmtls)
- ✅ ECDH + AES-GCM Encrypted Communication
- ✅ Block/Entity/Item Mapping
- ✅ Player State Synchronization
- ✅ Cross-Chat Message Intercommunication

---

## Architecture
```
src/
├── protocol/      # Protocol Layer
│   ├── mc_java.py    # Minecraft Java Protocol
│   ├── ilink.py      # iLink/mmtls Protocol
│   ├── raknet.py     # RakNet Adaptation
│   ├── mnw.py        # MiniWorld Protocol
│   └── business.py   # Business Protocol
├── crypto/        # Cryptography Layer (ECDH + HKDF + AES-GCM)
├── network/       # Network Layer (UDP + Session)
├── mapping/       # Mapping Layer (Block/Entity/Item/Coordinate)
└── bridge.py      # Core Bridge
```

---

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Bridge
```bash
python -m src.bridge
```

### Run Tests
```bash
python test_crypto_manual.py
python test_network_manual.py
python test_bridge_manual.py
python test_mc_java_manual.py
```

---

## Development Progress
- [x] Phase 1: Basic Framework
- [x] Phase 2: Cryptography Layer
- [x] Phase 3: Network Layer
- [x] Phase 4: Business Protocol Layer
- [x] Phase 5: Mapping Layer + Core Bridge
- [x] Phase 6: Minecraft Java Protocol
- [ ] Phase 7: Complete Online Multiplayer Features (In Development)

---

## Version History

| Version | Date | Description |
|------|------|------|
| 26w14a_main_26.89.0 | 2026-04-05 | Phase 1-6 Completed, Official Release |
| 26w14a_dev_26.1.6 | 2026-04-05 | Phase 6: MC Java Protocol |
| 26w14a_dev_26.1.5 | 2026-04-05 | Phase 5: Mapping Layer + Bridge |
| 26w14a_dev_26.1.4 | 2026-04-05 | Phase 4: Business Protocol Layer |
| 26w14a_dev_26.1.3 | 2026-04-05 | Phase 3: Network Layer |
| 26w14a_dev_26.1.2 | 2026-04-05 | Phase 2: Cryptography Layer |
| 26w14a_dev_26.1.1 | 2026-04-05 | Phase 1: Basic Framework |

---

## License
MIT License

---

## Contact
- Project Homepage: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
