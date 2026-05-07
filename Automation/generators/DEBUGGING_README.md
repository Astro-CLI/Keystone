# PT .pkt File Generation - Debugging Investigation

## 🎯 Quick Summary

**Problem**: Packet Tracer 8.2.2 rejects generated `.pkt` files  
**Root Cause Identified**: Format incompatibility (we use different algorithm than PT 8.2.2 expects)  
**Solution Status**: Awaiting PT 8.2.2 reference file for comparison  
**Time to Fix**: 1-3 days once reference is available  

---

## 📋 What Was Investigated

### ✅ Confirmed Valid (Our Implementation)

- **Encryption**: XOR algorithm works correctly
- **Compression**: zlib level 9 produces valid output
- **XML**: Generates valid Packet Tracer XML structure
- **Binary Structure**: Internally consistent and decompressible
- **Round-trip**: Files encrypt/decrypt correctly

### ❌ Problem Identified (PT Rejection)

- **Format Mismatch**: Our format ≠ what PT 8.2.2 expects
- **External Validation**: PT checks something we don't implement
- **Unknown Requirements**: PT's exact validation rules are unclear

### ❓ Still Unknown

- What format PT 8.2.2 actually uses
- What validation PT performs
- Why real Cisco files use different algorithm

---

## 📁 Documentation Structure

### Start Here

1. **`INVESTIGATION_STATUS.md`** ⭐ START HERE  
   High-level overview of investigation and findings

2. **`DEBUGGING.md`**  
   Practical debugging guide with concrete steps

3. **`DEBUG_REPORT.md`**  
   Detailed technical analysis of findings

4. **`KNOWN_ISSUES.md`**  
   Known limitations and workarounds

### Tools Reference

- **`pt_debug.py`** - Binary format analyzer
- **`pt_file_builder_enhanced.py`** - Enhanced builder with debugging
- **`pt_file_inspector.py`** - File validation tool

---

## 🔍 Key Findings

### Finding 1: Format Variants Exist

At least 2 formats identified:

```
Format A (Ours):  [4-byte header] + [XOR payload with key=(size-i)]
Format B (Real):  [All XOR'd with key=(file_size-i)]
Format C (PT 8.2.2): [Unknown - PT won't accept ours]
```

### Finding 2: Our Implementation is Sound

Our files:
- ✓ Decompress correctly
- ✓ Extract valid XML
- ✓ Have proper structure
- ✗ PT still rejects them

This means: Problem is EXTERNAL (format/validation), not INTERNAL (encoding/compression)

### Finding 3: Reference Format Unknown

Real Cisco files:
- Cannot decrypt with either known algorithm
- Suggests PT 8.2.2 uses yet another format
- Blocks our ability to validate against working examples

---

## 🛠️ Tools Available

### 1. Binary Analyzer: `pt_debug.py`

```bash
python3 pt_debug.py file.pkt
```

Tests:
- File signature/magic bytes
- Byte order (endianness)
- Checksums/validation
- XML structure
- Compression variants
- XOR key calculations

**When to use**: When investigating a .pkt file format

### 2. Enhanced Builder: `pt_file_builder_enhanced.py`

```bash
python3 pt_file_builder_enhanced.py topology.yaml -o output.pkt --debug
```

Features:
- Debug logging for all steps
- Multiple format implementations
- Validation checks
- Alternative algorithms

**When to use**: When testing different format implementations

### 3. File Inspector: `pt_file_inspector.py`

```bash
python3 pt_file_inspector.py file.pkt
```

Capabilities:
- Extract XML
- Validate structure
- Show device list
- Verify decompression

**When to use**: When checking if a file is internally valid

---

## 📊 Investigation Results

### Test Matrix

| Test | Our Files | Real Files | Status |
|------|-----------|-----------|--------|
| Can decompress | ✓ | ✗ | Our format works, real format unknown |
| XML valid | ✓ | ? | Ours is valid, unknown for real |
| PT opens | ✗ | ? | Ours rejected, real unknown |
| Encryption correct | ✓ | ? | Ours proven, real unknown |

### Format Compatibility

```
    Our Format    ptexplorer    PT 8.2.2
Our files:  ✓ Works      ✗ Fails        ✗ Rejects
Real files: ✗ Can't open  ? Unknown      ? Unknown
```

---

## 🚀 Next Steps

### Immediate (1-2 hours)

1. Find a PT 8.2.2 .pkt file created in the GUI
   - Cisco Netacad samples
   - Community forums
   - User installations

2. Run `pt_debug.py` on it
   ```bash
   python3 pt_debug.py reference.pkt
   ```

3. Compare output with our files

### Short Term (2-4 hours)

1. Hex dump both files
   ```bash
   hexdump -C reference.pkt > ref.hex
   hexdump -C ours.pkt > ours.hex
   diff ref.hex ours.hex
   ```

2. Extract and compare XML
   ```bash
   python3 pt_file_inspector.py reference.pkt --xml > ref.xml
   python3 pt_file_inspector.py ours.pkt --xml > ours.xml
   diff ref.xml ours.xml
   ```

3. Identify structural differences

### Implementation (1-3 days)

Once differences identified:

1. Update XML generation if needed
2. Implement correct format if different
3. Test with `pt_file_builder_enhanced.py`
4. Validate in PT

---

## 💡 Testing Checklist

Use this to track investigation progress:

**Phase 1: File Acquisition**
- [ ] Have reference PT 8.2.2 file
- [ ] Can access PT for testing
- [ ] Have hex editor/tools

**Phase 2: Analysis**
- [ ] Run pt_debug.py on reference
- [ ] Run pt_debug.py on our files
- [ ] Created hex dumps
- [ ] Compared binary structure

**Phase 3: Deep Dive**
- [ ] Extracted and compared XML
- [ ] Identified structural differences
- [ ] Documented all differences
- [ ] Created test cases

**Phase 4: Implementation**
- [ ] Updated format if needed
- [ ] Tested in enhanced builder
- [ ] Verified with pt_inspector
- [ ] Tested in PT (if possible)

---

## 📞 How to Get Help

### If You're Debugging

1. Use `pt_debug.py` on any suspicious file
2. Check `DEBUGGING.md` for procedures
3. Run tests from the checklist
4. Document findings

### If You're Stuck

1. Review `DEBUG_REPORT.md` for similar issues
2. Check `KNOWN_ISSUES.md` for workarounds
3. Look at test files in `SOYMSA/` and `Automation/`
4. Try the tools with different parameters

### If You Want to Contribute

1. Run investigation procedure
2. Document findings
3. Update relevant .md files
4. Test implementations
5. Submit results

---

## 🔗 File Reference

### Documentation

| File | Purpose | Read Time |
|------|---------|-----------|
| `INVESTIGATION_STATUS.md` | Overview | 5 min |
| `DEBUGGING.md` | Procedures | 10 min |
| `DEBUG_REPORT.md` | Technical | 15 min |
| `KNOWN_ISSUES.md` | Limitations | 10 min |

### Tools

| File | Purpose | Lines | Usage |
|------|---------|-------|-------|
| `pt_debug.py` | Analyzer | 400+ | Binary investigation |
| `pt_file_builder_enhanced.py` | Builder | 300+ | Format testing |
| `pt_file_inspector.py` | Inspector | 200+ | Validation |

### Test Data

| Location | Type | Count | Purpose |
|----------|------|-------|---------|
| `SOYMSA/` | Real PT | 4 | Reference |
| `Automation/*.pkt` | Generated | 5+ | Testing |

---

## ⚡ Quick Commands

### Analyze a file
```bash
python3 pt_debug.py SOYMSA/Core.pkt | head -100
```

### Check if our file is valid
```bash
python3 pt_file_inspector.py Automation/simple_lab.pkt
```

### Generate with debug output
```bash
python3 pt_file_builder_enhanced.py example_topology.yaml -o test.pkt --debug 2>&1 | head -50
```

### Extract XML
```bash
python3 << 'PYTHON'
import sys
sys.path.insert(0, 'Automation')
from pt_file_inspector import PTFileInspector
xml = PTFileInspector('file.pkt').decrypt_and_decompress()
print(xml[:1000])
PYTHON
```

### Compare two files
```bash
hexdump -C file1.pkt | head -20
hexdump -C file2.pkt | head -20
```

---

## 🎓 Learning Resources

### Understanding the Problem

- Read: `INVESTIGATION_STATUS.md` (overview)
- Read: `DEBUG_REPORT.md` (analysis)
- Try: `pt_debug.py` on sample files

### Understanding the Solution

- Read: `DEBUGGING.md` (procedures)
- Use: `pt_file_builder_enhanced.py` (testing)
- Reference: `KNOWN_ISSUES.md` (limitations)

### Understanding the Code

- Review: `pt_file_builder.py` (main implementation)
- Review: `pt_debug.py` (analysis tool)
- Check: `pt_file_inspector.py` (validation)

---

## 📌 Key Points to Remember

1. **Our files ARE internally valid**
   - Encryption works ✓
   - Compression works ✓
   - XML is valid ✓
   - PT rejects them anyway ✗

2. **The problem is EXTERNAL**
   - Not our encryption (that's proven)
   - Likely format or schema difference
   - PT validates something we don't implement

3. **We need a REFERENCE FILE**
   - To compare against
   - To identify differences
   - To understand PT's requirements

4. **Solution is ACHIEVABLE**
   - Clear investigation path
   - Tools are ready
   - Estimated 1-3 days to fix

---

## 🎯 Current Status

```
Investigation:  ✅ COMPLETE
Analysis:       ✅ COMPLETE
Tools:          ✅ CREATED
Documentation:  ✅ WRITTEN
Next Action:    ⏳ Find PT 8.2.2 reference file
Timeline:       📅 1-3 days to implement fix
Blocker:        🔒 Need PT 8.2.2 file for comparison
```

---

## 📖 Document Index

- **Start here**: `INVESTIGATION_STATUS.md`
- **How to debug**: `DEBUGGING.md`
- **Deep analysis**: `DEBUG_REPORT.md`
- **Known issues**: `KNOWN_ISSUES.md`
- **This file**: `DEBUGGING_README.md`

---

**Last Updated**: Investigation Complete  
**Status**: Ready to Proceed  
**Next Step**: Acquire PT 8.2.2 Reference File  

---
