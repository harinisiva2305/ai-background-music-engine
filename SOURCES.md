# Audio Sources and Licensing

## 1. Current Audio Generation Method

The current prototype synthesizes audio procedurally using Python, NumPy, and SciPy. It generates audio waveforms in code rather than using downloaded music recordings or instrument samples.

| Component | Current source | Licensing notes |
|---|---|---|
| Harmony | Procedural synthesis in `app/generate_demo.py` | No external audio recording currently identified |
| Bass | Procedural synthesis in `app/generate_demo.py` | No external audio recording currently identified |
| Melody | Procedural synthesis in `app/generate_demo.py` | No external audio recording currently identified |
| Drums | Procedural synthesis in `app/generate_demo.py` | No external audio recording currently identified |

## 2. Software Dependencies

The prototype uses open-source Python packages, including NumPy, SciPy, FastAPI, and Uvicorn.

- NumPy: https://github.com/numpy/numpy
- SciPy: https://github.com/scipy/scipy
- FastAPI: https://github.com/fastapi/fastapi
- Uvicorn: https://github.com/encode/uvicorn

Each dependency has its own license. Review the applicable license and version before distributing the project.

## 3. Third-Party Audio Assets

**Current status:** No third-party audio samples or SoundFont files are intentionally included in the current procedural generator.

If a SoundFont, sample library, or other audio asset is added later, record the following before using it:

- Asset name and download URL
- Creator or copyright holder
- Exact license and license URL
- Required attribution or notices
- Confirmation that commercial use and modification are permitted
- Any redistribution restrictions

## 4. Commercial-Use Verification

The current audio is synthesized by the project's own code. This does not automatically establish that the entire project is cleared for commercial distribution. Review the licenses of the software dependencies and any future assets, and verify any applicable legal requirements before commercial use.

No unverified third-party audio asset is claimed to be commercially licensed by this document.
