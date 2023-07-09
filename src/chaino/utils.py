import json

import pandas as pd


def convert_json_to_csv(in_file):
    with open(in_file) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv(in_file.replace('.json', '.csv'), index=False)
