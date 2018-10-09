import json
with open('build_config.json', 'r') as infile:
    _input = json.load(infile)
with open('build_config2.json', 'w') as outfile:
    json.dump(_input, outfile, indent=4)
