# PT .pkt Format Debugging Guide

## Problem Statement

Generated `.pkt` files are rejected by Packet Tracer 8.2.2 with error:
```
"Unable to open file. The file was not saved correctly."
```

However:
- Files decompress correctly ✓
- XML extracts successfully ✓  
- Binary structure is valid ✓
- Files are not corrupted ✓

**Conclusion**: PT is validating something we're not implementing.

---

## Critical Discovery: Format Uncertainty

We discovered the binary format is **not definitively established** for PT 8.2.2:

### What We Know (Confirmed)
1. Our algorithm works: `header (4 bytes) + XOR-encrypted payload`
2. Payload contains: zlib-compressed XML
3. XML can be extracted and parsed

### What We Don't Know (Blocking)
1. Is this the correct format for PT 8.2.2?
2. Does PT validate XML schema strictly?
3. Are there required XML elements we're missing?
4. Does PT require file signatures or metadata?
5. Why do real Cisco PT files use a different format?

---

## Test Matrix: What Works and What Doesn't

### Format Compatibility

```
Format              Algorithm                  Our Files   Real Files
─────────────────────────────────────────────────────────────────────
Our Implementation  size-based XOR+header      ✓ Works     ✗ Fails
ptexplorer Format   file-size-based XOR        ✗ Fails     ❓ Unknown
PT 8.2.2 Format     ??? (Unknown)              ❓ Rejects   ❓ Unknown
```

### What This Means
- Our implementation is internally consistent
- But we don't know if it matches what PT 8.2.2 expects
- Real Cisco PT files use a completely different algorithm
- **The gap between "internally valid" and "PT-compatible" is unknown**

---

## Debugging Approach: Priority Order

### Phase 1: Validate Against Working Examples (1-2 hours)

**Objective**: Get a working reference implementation

**Steps**:
1. **Find PT 8.2.2 test file**
   ```bash
   # Try different sources:
   - Cisco Netacad sample files
   - PT 8.2.2 default templates
   - Community-shared files
   ```

2. **Analyze with multiple tools**
   ```bash
   python3 pt_debug.py reference_file.pkt
   python3 pt_file_inspector.py reference_file.pkt
   file reference_file.pkt
   xxd reference_file.pkt | head -50
   ```

3. **Compare with our generated file**
   ```bash
   # Side-by-side comparison
   hexdump -C our_generated.pkt > our.hex
   hexdump -C reference.pkt > ref.hex
   diff our.hex ref.hex | head -100
   ```

4. **Extract and compare XML**
   ```bash
   python3 pt_file_inspector.py reference_file.pkt --xml > ref.xml
   python3 pt_file_inspector.py our_generated.pkt --xml > our.xml
   diff ref.xml our.xml
   ```

### Phase 2: XML Schema Analysis (2-4 hours)

**Objective**: Identify missing or incorrect XML elements

**Comparison Points**:
- Root element attributes (`version`, `build`, others?)
- Required child elements
- Network/ObjectGroup/ConnectionGroup structure
- Device attributes and properties
- Interface structure
- Configuration requirements

**Example Investigation**:
```python
# Check for missing elements
import xml.etree.ElementTree as ET

ref_xml = ET.parse('ref.xml').getroot()
our_xml = ET.parse('our.xml').getroot()

ref_elements = set(elem.tag for elem in ref_xml.iter())
our_elements = set(elem.tag for elem in our_xml.iter())

missing = ref_elements - our_elements
extra = our_elements - ref_elements

print("Missing elements:", missing)
print("Extra elements:", extra)
```

### Phase 3: Encryption Algorithm Verification (1-2 hours)

**Objective**: Confirm we're using the right algorithm for PT 8.2.2

**Method**:
```python
# If we have a PT-created file:
1. Manually create a file in PT 8.2.2
2. Try to decrypt with our algorithm
3. If it works: Format is confirmed ✓
4. If it fails: Algorithm is wrong ✗
```

**Alternative Method**:
```python
# Brute force parameter search
for compression_level in range(0, 10):
    for xor_key_formula in [variations]:
        for header_format in [variations]:
            try:
                # Test if PT can open
```

### Phase 4: Version-Specific Investigation (2-3 hours)

**Objective**: Determine if PT 8.2.2 has specific format requirements

**Investigation Points**:
- PT 8.2.2 release notes for format changes
- Difference between PT 8.2.2 and PT 8.3.x
- PT source code analysis (if available)
- Community discussions/forums

**Locations to Search**:
- Cisco Netacad forums
- Stack Overflow (PT tags)
- GitHub discussions
- Cisco community resources

---

## Root Cause Hypothesis: The Most Likely Explanation

### Theory: PT Validates XML Schema

**Why this is likely**:
- PT can extract XML even if it's malformed
- PT would reject if XML is "not saved correctly" when attributes are missing
- Our XML may be missing required elements

**Elements We Should Check**:
```xml
<PacketTracer>
  <!-- Required? -->
  <Version>?</Version>
  <Build>?</Build>
  <Created>?</Created>
  <Modified>?</Modified>
  
  <Network>
    <ObjectGroup>
      <Device>
        <!-- Required? -->
        <Property name="type">?</Property>
        <Property name="model">?</Property>
        <Property name="os">?</Property>
        <Property name="ios_version">?</Property>
      </Device>
    </ObjectGroup>
  </Network>
</PacketTracer>
```

### Theory: PT 8.2.2 Uses Different Format

**Why this is possible**:
- ptexplorer was written for PT 5.x
- PT has evolved significantly since then  
- Real Cisco files we tested use different algorithm
- Our algorithm is custom (not from official source)

**Evidence**:
- Cannot decrypt SOYMSA files
- Cannot apply ptexplorer algorithm to our files
- Two different algorithms exist but don't both work

---

## Concrete Testing Steps (Try These)

### Step 1: Create Minimal Test Case

```python
import sys
sys.path.insert(0, 'Automation')
from pt_file_builder import PTFileBuilder

# Absolute minimal topology
minimal = {
    'devices': [{
        'hostname': 'Router1',
        'type': 'router',
        'interfaces': [{
            'name': 'GigabitEthernet0/0/0',
            'ip': '192.168.1.1',
            'mask': '255.255.255.0'
        }]
    }]
}

builder = PTFileBuilder(minimal)
builder.save_pkt_file('minimal_test.pkt')
```

Then try to open in PT 8.2.2. If it fails, gradually add elements:
- Add second device
- Add connection/link
- Add OSPF config
- Add hostname
- etc.

### Step 2: Try Multiple Topologies

```bash
python3 pt_file_builder.py example_topology.yaml -o test1.pkt
python3 pt_file_builder.py complex_topology.yaml -o test2.pkt
python3 pt_file_builder.py large_network.yaml -o test3.pkt
```

Test each in PT and note if ANY work, or if ALL fail.

### Step 3: Compare File Sizes

```bash
ls -lh *.pkt SOYMSA/*.pkt | awk '{print $5, $9}' | sort -h
```

Look for patterns:
- Are PT-created files always larger/smaller?
- Is there a ratio between uncompressed and compressed?

---

## Resolution Paths (Ranked by Viability)

### Path A: Reverse-Engineer PT 8.2.2 (BEST, but expensive)

**Process**:
1. Get PT 8.2.2 application binary
2. Use debugger to trace file loading
3. Find encryption/decompression routine
4. Reverse-engineer the algorithm

**Time**: 3-5 days
**Success**: Very high (95%+)
**Tools needed**: Debugger (IDA Pro, Ghidra, etc.)
**Cost**: May require paid tools

### Path B: Use ptexplorer as Backend (SAFE, proven)

**Process**:
1. Call ptexplorer command-line tool
2. Or use its Python library
3. Generate files through validated implementation

**Time**: 1-2 days
**Success**: High (90%+)
**Tools needed**: ptexplorer (free)
**Limitation**: Dependency on external tool

### Path C: Improve XML Structure (HOPE-BASED)

**Process**:
1. Add more elements to our XML
2. Test if PT accepts them
3. Iteratively improve

**Time**: 2-3 days
**Success**: Unknown (20-40%)
**Tools needed**: None
**Risk**: May waste time if that's not the issue

### Path D: Find PT 8.2.2 Documentation (IF EXISTS)

**Process**:
1. Search for official Cisco format documentation
2. Check academic papers/theses  
3. Contact Cisco directly

**Time**: 1-2 days
**Success**: Unknown (5-15%)
**Tools needed**: Search skills
**Limitation**: Unlikely to exist

---

## Recommended Approach

### Immediate (Do Now)
1. ✅ Complete debugging investigation (**DONE - this file**)
2. ✅ Create debug tools (`pt_debug.py` **CREATED**)
3. ✅ Generate test files (we have several)
4. ⏭️ Try to find a reference PT 8.2.2 file

### Short Term (Next)
1. If we find reference file: Compare byte-by-byte
2. If no reference file: Try ptexplorer backend approach
3. Test with someone who has PT 8.2.2 installed

### Medium Term (If needed)
1. Implement format improvements based on findings
2. Add schema validation
3. Create enhanced XML generation

### Long Term (If still not working)
1. Reverse-engineer via binary analysis
2. Contact Cisco/Netacad
3. Switch to ptexplorer as definitive implementation

---

## How to Use This Guide

**For Developers**:
- Follow "Testing Steps" to identify the actual issue
- Use "Resolution Paths" to plan implementation
- Consult "Root Cause Hypothesis" to guide investigation

**For Users**:
- Understand that "internally valid" ≠ "PT-compatible"
- Tools like `pt_file_inspector.py` can verify structure
- Cannot generate PT-compatible files yet (status: investigating)

**For Contributors**:
- This is an active investigation
- Help with any of the "Concrete Testing Steps"
- Look for reference PT files
- Test with PT instances you have access to

---

## Known Status

| Component | Status | Notes |
|-----------|--------|-------|
| Binary format | ❓ Unknown | Works internally, rejected by PT |
| Encryption | ✓ Verified | Works for our format |
| Compression | ✓ Verified | zlib level 9 |
| XML generation | ✓ Valid | Extracts correctly |
| PT 8.2.2 opening files | ✗ Failing | Error: "not saved correctly" |
| Format documentation | ❓ Uncertain | ptexplorer may be outdated |
| Real Cisco files | ❓ Undecrypted | Different algorithm |

---

## Questions for Investigation

1. **Can we find a PT 8.2.2 file created in the GUI?**
   - YES → Compare directly
   - NO → Contact community

2. **Does ptexplorer work on PT 8.2.2 files?**
   - YES → Use that code as reference
   - NO → Format has changed

3. **Can we access PT source or documentation?**
   - YES → Implement correctly  
   - NO → Reverse-engineering needed

4. **Are there PT format changes between versions?**
   - YES → Version-specific fixes needed
   - NO → Same format should work

---

## Resources

- **ptexplorer**: https://github.com/axcheron/ptexplorer
- **packetReader**: https://github.com/joeyfrontend/packetReader
- **This project**: `pt_file_builder.py` and `pt_debug.py`
- **Our debug report**: `DEBUG_REPORT.md`
- **Test files**: `SOYMSA/*.pkt` (real) and `Automation/*.pkt` (generated)

---

## Conclusion

We have created a functioning .pkt file generator that:
- ✓ Correctly encrypts and compresses XML
- ✓ Generates valid Packet Tracer XML structure
- ✓ Can be inspected and verified

But we cannot confirm:
- ✗ That our format matches PT 8.2.2 expectations
- ✗ That XML schema is complete
- ✗ Why PT rejects the files

**Next step**: Obtain a reference PT 8.2.2 file and analyze it.

