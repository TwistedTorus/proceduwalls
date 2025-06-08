import argparse
import json

from ruin import Ruin, plot_ruin, generate_svgs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = "Ruin Builder")
    parser.add_argument("--input", type=str, required = True)
    parser.add_argument("--mode", type=str, choices = ["svg", "plot"], default = "svg")
    args = parser.parse_args()

    input_file = args.input
    mode = args.mode
    output = "/tmp/output.json"

    with open(input_file, "r") as f:
        input_data = json.load(f)

    wall_code = input_data["wall_code"]
    floor_codes = input_data["floor_codes"]
    x = input_data["length"]
    y = input_data["width"]
    z = input_data["height"]
    dimensions = (x,y,z)
    resolution = input_data["segments_per_wall"]

    ruin = Ruin(dimensions, resolution)
    ruin.generate_from_build_code(wall_code, floor_codes)

    match mode:
        case "svg":
            wall_svgs, floor_svgs, full_svg = generate_svgs(ruin)

            #data_dict = { "walls" : [str(w) for w in wall_svgs], "floors" : [str(f) for f in floor_svgs], "full" : str(full_svg) }
            #with open(output, "w") as f:
            #    f.write(json.dumps(data_dict))

            print(full_svg)

        case "plot":
            plot_ruin(ruin)
        case _:
            pass
