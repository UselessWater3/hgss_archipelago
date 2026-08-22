# Pokémon HeartGold and SoulSilver Archipelago (AP)

The setup guide is [here](docs/setup_en.md).

## Running From Source
Additionally to what Archipelago requires, the `pyparsing` library is required.
This can be installed via PIP.

With the dependencies installed,
clone this repository in the `worlds` directory of the Archipelago repository,
and rename the repository root's folder to `pokemon_hgss`.
With every modification to the files in `data_gen` or `data_gen_templates`, and when first cloning the
repository, the `data_gen.py` file must be executed. (Do `python data_gen.py` in the root directory of the repository)

To make the `.apworld` file, run `make` within the root directory of the repository.
This is expecting standard UNIX utilities (`make`, `if`, `curl`, `rm`, `tar`, `echo`).
On Windows, it is recommended to run this through Git Bash or WSL.

If you don't have standard UNIX utilities, you can make it manually as follows. First,
download the release of [apnds](https://github.com/ljtpetersen/apnds) corresponding to
the version in the [`apnds_version.txt`](apnds_version.txt) file. Extract the output into the root of the repository.
Run the data generation (`python data_gen.py` in the root of the repository).
Afterwards, in the Archipelago Launcher, run the Build APWorlds option.

## Credits
* Thanks to [Linneus](https://github.com/Linneus), [Seafo](https://github.com/Seatori), [AtomicPurpleGB](https://github.com/FLMBorges), and PsychoDon525 for help with the rules and labels.
* Thanks to [Linneus](https://github.com/Linneus) for creating awesome art!
* Thanks to [gerbiljames](https://github.com/gerbiljames) for help with structuring the client and world and miscellaneous
  tech support.

## AI Usage Disclosure
* This project (both the world and the client) contains **no** AI-generated code.
* This project contains **no** AI-generated art.
* LLMs have been used for debugging obscure issues, but they were of **NO** help.
* Pull requests by other contributors, which may contain AI-generated code, are reviewed for correctness before being merged.

