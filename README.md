# ComfyUI-IsolationTest

Test suite and analysis tools for PyIsolate integration in ComfyUI.

## Installation

```bash
cd ComfyUI/custom_nodes
git clone <repo-url> ComfyUI-IsolationTest
cd ComfyUI-IsolationTest
pip install -r requirements.txt
```

## Nodes

### TestCLIPProxy
Full CLIP proxy test - tokenize + encode + conditioning validation.

### TestCLIPProxySimple  
Minimal CLIP test - tokenize only, no tensor operations.

### RunIsolationTests
Runs unit tests for route injection and PyIsolate integration.

## Usage

1. Enable isolation: Ensure `pyisolate.yaml` exists
2. Add test node to workflow
3. Execute and check report output

## Requirements

- ComfyUI with PyIsolate integration
- Python 3.10+
