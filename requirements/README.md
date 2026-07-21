# Reproducible environments

The `.in` files are maintained inputs. Their `.txt` counterparts are
hash-pinned sets, and each generated header records the interpreter version.
The `.txt` extension is used because `.lock` files are not stored in the
OneDrive workspace. Generate the runtime, CI, and release sets on Linux with
Python 3.12 so platform-conditional dependencies match the runner.

Regenerate with `pip-compile --generate-hashes --resolver=backtracking
--strip-extras --no-emit-index-url --no-emit-trusted-host`, and install with:

```powershell
python -m pip install --require-hashes -r requirements/runtime.txt
```

Regenerate and audit the sets on every dependency change. Add
Python-version-specific `.txt` sets if supported interpreters resolve
materially different graphs.

The Linux runtime, CI, and release sets can be reproduced from the repository
root with:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace python:3.12-slim sh -c 'python -m pip install "pip-tools>=7.5,<8" && pip-compile --generate-hashes --resolver=backtracking --strip-extras --no-emit-index-url --no-emit-trusted-host requirements/runtime.in -o requirements/runtime.txt && pip-compile --generate-hashes --resolver=backtracking --strip-extras --no-emit-index-url --no-emit-trusted-host requirements/test.in -o requirements/test.txt && pip-compile --generate-hashes --resolver=backtracking --strip-extras --no-emit-index-url --no-emit-trusted-host requirements/release.in -o requirements/release.txt'
```
