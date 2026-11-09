#!/usr/bin/env python

import calendar
import copy
import os
import subprocess

#import sys
from pathlib import Path

from ruamel.yaml import YAML
from pyprojroot import here
# Get project root
root_path = Path(here())

yaml=YAML()
with open(root_path.joinpath('recipe.yml')) as f:
    cfg = yaml.load(f)
    experiment = cfg["experiment"]
    workdir = cfg["workdir"]

    caseid = experiment["caseid"]
    input_root = experiment["input_root"]
    year_start = experiment["year_start"]
    year_end = experiment["year_end"]

    work_root = workdir["work_root"]
    overwrite = workdir["overwrite"]

    variables = cfg["variables"]
    
# define the frequency mapping for each tag
freq={"hy": "yearly", "hm": "monthly",
      "hbgcy": "yearly", "hbgcm": "monthly",
      "h":"monthly", "h1":"daily"}
realm = {
    "blom": "ocn",
    "cice": "ice",
}

# Save generated climatology information to a YAML file
settings_file = "notebooks/settings.yml"
with open(root_path.joinpath(settings_file), "r") as f:
    settings = yaml.load(f)

settings["climos"] = {
    "blom": {
        "hy": {},
        "hm": {},
        "hbgcy": {},
        "hbgcm": {},
    },
    "cice": {
        "h": {},
        "h1": {},
    }
}
settings["timeseries"] = copy.deepcopy(settings["climos"])

# Common configuration based on your ncclimo output
suffix = "climo.nc"

# Define seasons with their respective start and end months (ncclimo standard)
seasons_meta = {
    "ANN": ("01", "12"),
    "DJF": ("01", "12"),  # ncclimo typically sets DJF to the full year span
    "MAM": ("03", "05"),
    "JJA": ("06", "08"),
    "SON": ("09", "11"),
}


# Optional: ensure system NCO is used, not a user-overridden version
env = os.environ.copy()
env['NCO_PATH_OVERRIDE'] = 'No'

for model, tags in variables.items():       # model: [blom, cice]
    for tag, varlist in tags.items():         # tag: [hy, hm, hbgcy, hbgcm]
        climo = varlist["climo"]
        if not climo:
            continue
        print("----------------------------------")
        print(f"Process: {model}, {tag}, {climo}")
        # ncclimo arguments
        args = [
            "nco/ncclimo",
            "-m", model,
            "-h", tag,
            f"--clm_md={freq[tag]}",
            "-c", cfg['experiment']['caseid'],
            "-i", f"{input_root}/{caseid}/{realm[model]}/hist",
            "-o", f"{work_root}/{caseid}/{model}.{tag}",
            "-s", str(year_start),
            "-e", str(year_end),
            "-v", ",".join(climo),
            "-p", "background",
            "-j", "12"              
        ]

        if overwrite is True:
            # Execute ncclimo
            print(" ".join(args))
            process = subprocess.run(
                args,
                check=False,
               #capture_output=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )
            # Check for success
            if process.returncode == 0:
                print("Climatology generated successfully.")
            else:
                print("\nERROR: Climatology generation failed.")
                print(process.stdout)
        else:
            print("Skip computing existing climotologies..")

        # Monthly files (01 to 12)
        for i in range(1, 13):
            m = f"{i:02d}"
            mth = calendar.month_abbr[i].upper()
            fname = f"{caseid}_{m}_{year_start}{m}_{year_end}{m}_{suffix}"
            settings['climos'][model][tag][mth] = f"{work_root}/{caseid}/{model}.{tag}/{fname}"
        
        # Seasonal files
        for climo_period, (start_m, end_m) in seasons_meta.items():
            fname = f"{caseid}_{climo_period}_{year_start}{start_m}_{year_end}{end_m}_{suffix}"
            settings['climos'][model][tag][climo_period] = f"{work_root}/{caseid}/{model}.{tag}/{fname}"

        # ANN files
        start_m, end_m = seasons_meta["ANN"]
        fname = f"{caseid}_ANN_{year_start}{start_m}_{year_end}{end_m}_{suffix}"
        settings['climos'][model][tag]['ANN'] = f"{work_root}/{caseid}/{model}.{tag}/{fname}"

# Write the structure to a YAML file
with open(root_path.joinpath(settings_file), "w") as f:
    yaml.dump(settings, f)
