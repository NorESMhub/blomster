from collections import defaultdict

import yaml

# Load ----
with open('diagnostics.yml', 'r') as f:
    data = yaml.safe_load(f)

# ---- 2. Pull out the top-level defaults BEFORE stripping section 'vars' ----
defaults = data.pop('vars', {}) or {}
# ---- 3. Collect section-level vars, grouped by category ----
collected_vars = defaultdict(set)   # set → auto-dedupe

def collect_vars(node):
    """Walk the tree and collect every nested 'vars' dict, merging by category."""
    if isinstance(node, dict):
        if 'vars' in node and isinstance(node['vars'], dict):
            for category, values in node['vars'].items():
                if isinstance(values, list):
                    collected_vars[category].update(values)
                elif values is not None:
                    collected_vars[category].add(values)
        for value in node.values():
            collect_vars(value)
    elif isinstance(node, list):
        for item in node:
            collect_vars(item)

# ---- 4. Strip section-level 'vars' keys ----
def strip_vars(node):
    if isinstance(node, dict):
        node.pop('vars', None)
        for value in node.values():
            strip_vars(value)
    elif isinstance(node, list):
        for item in node:
            strip_vars(item)

collect_vars(data)
strip_vars(data)

# ---- 5. Merge defaults + collected (defaults first, preserving order) ----
merged_vars = {}
for category in set(defaults) | set(collected_vars):
    merged = list(defaults.get(category, []) or [])
    for v in collected_vars.get(category, []):
        if v not in merged:
            merged.append(v)
    merged_vars[category] = merged

# ---- 6. Reassemble: 'vars' first, then 'chapters' ----
output = {'vars': merged_vars, **data}


#with open('../_toc.yml', 'r') as f:
#    toc = yaml.safe_load(f)
#
#print(toc)

toc = {}
toc['format'] = 'jb-book'
toc['root'] = 'index'
toc['chapters'] = data['chapters']

# ---- 7. Write ----
with open('_toc.yml', 'w') as f:
    yaml.dump(toc, f, default_flow_style=False, sort_keys=False)

# ---- 8. Report ----
print("Merged vars:")
for k, v in merged_vars.items():
    print(f"  {k}: {v}")

print("\nCollected from sections:")
for k, v in collected_vars.items():
    print(f"  {k}: {sorted(v)}")
