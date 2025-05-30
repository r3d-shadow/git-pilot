import os

def write_file(path: str, content: str) -> None:
    """
    Helper to write a file to disk, creating parent dirs as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def write_example_structure(root_dir: str) -> None:
    files = {
        os.path.join(root_dir, 'example.yml.j2'): """\
name: [[ ci_name ]]

on:
  push:
    branches:
      - "[[ env ]]"

jobs:
  [[ job_id ]]:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      [[ include('units/hello-world.j2') | indent(6) ]]
""",

        os.path.join(root_dir, 'override-example.yml.j2'): """\
name: [[ ci_name ]]

on:
  push:
    branches:
      - "[[ env ]]"

jobs:
  [[ job_id ]]:
    runs-on: ubuntu-latest
    steps:
      - name: Hello from [[ env ]]!
        run: echo "Hello, [[ job_id ]]!"
        env:
          SUPER_SECRET: ${{ secrets.SuperSecret }}
""",

        os.path.join(root_dir, 'includes', '_helpers.tpl'): """\
[%- macro upper(s) -%]
[[ s.upper().strip() if s ]]
[%- endmacro -%]
""",

        os.path.join(root_dir, 'includes', 'units', 'hello-world.j2'): """\
- name: Hello World
  run: echo "Hello, World from job [[ _.upper(job_id) ]]!"
""",

        os.path.join(root_dir, 'values.yml'): """\
defaults:
  branch: dev
  message: "git-pilot: update CI workflow"
  path: ".github/workflows"
  vars:
    ci_name: scan
  templates:
    - ".*\\\\.j2$"

repos:
  - name: r3d-shadow/git-pilot-test-1
    vars:
      job_id: container_scan1
      env: test

  - name: r3d-shadow/git-pilot-test-2
    branch: main
    message: "git-pilot: update CI workflow : Override"
    path: ".github/workflows/git-pilot/"
    vars:
      job_id: sast_scan123456
      env: stage
    templates:
      - "^override.*\\\\.j2$"
"""
    }

    for path, content in files.items():
        write_file(path, content)