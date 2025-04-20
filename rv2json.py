import io
import struct
import json
import yaml
import argparse
from rubymarshal.reader import loads
from rubymarshal.classes import RubyObject, UserDef

def _serialize_obj(converted_obj, orig_obj):
    if type(orig_obj) != RubyObject:
        obj_type_name = orig_obj.__class__.__name__
    else:
        obj_type_name = orig_obj.ruby_class_name

    return {"val": converted_obj, "type": obj_type_name}

class Table:
    tile_size = 2

    def __init__(self, table_obj):
        self.table_obj = table_obj
        self.dim = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.unknown = 0
        self.data = []

        fd = io.BytesIO(table_obj._private_data)
        self.dim = struct.unpack("i", fd.read(4))[0]
        self.x = struct.unpack("i", fd.read(4))[0]
        self.y = struct.unpack("i", fd.read(4))[0]
        self.z = struct.unpack("i", fd.read(4))[0]
        self.unknown = struct.unpack("i", fd.read(4))[0]
        
        for _ in range(self.y * self.z):
            table_row = struct.unpack("%dH" % self.x, fd.read(self.tile_size * self.x))
            self.data.append(table_row)

    def serialize(self):
        obj = {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "unknown": self.unknown,
            "data": self.data
        }

        for k in obj:
            obj[k] = _serialize_obj(obj[k], obj[k])

        return obj

class RVDataFile:
    def __init__(self):
        self._data = {}

    def from_rvdata(self, input_file):
        self._data = self._rvdata2dict(loads(open(input_file, "rb").read()))

    def from_json(self, input_file):
        with open(input_file, 'r') as f:
            self._data = json.load(f)

    def to_rvdata(self, output_file):
        # Placeholder for RVData writing functionality
        pass

    def to_json(self, output_file):
        json_data = json.dumps(self._data, indent=4, sort_keys=True)
        with open(output_file, "w") as f:
            f.write(json_data)

    def to_yaml(self, output_file):
        with open(output_file, 'w') as f:
            yaml.dump(self._data, f, default_flow_style=False)

    def _rvdata2dict(self, rvdata_obj, serialize=True):
        res = {}

        if not hasattr(rvdata_obj, "attributes") and type(rvdata_obj) not in [dict, list]:
            return rvdata_obj

        child_nodes = rvdata_obj.attributes if hasattr(rvdata_obj, "attributes") else rvdata_obj

        if isinstance(child_nodes, list):
            res = []

        for attr in child_nodes:
            inner_obj = child_nodes[attr] if not isinstance(child_nodes, list) else attr
            inner_obj_type = type(inner_obj)

            if not hasattr(inner_obj, "attributes") and inner_obj_type not in [dict, list]:
                converted_obj = inner_obj if inner_obj_type != bytes else repr(inner_obj)

                if not isinstance(child_nodes, list):
                    res[attr] = _serialize_obj(converted_obj, inner_obj)
                else:
                    res.append(_serialize_obj(converted_obj, inner_obj))
                continue

            if isinstance(inner_obj, UserDef) and inner_obj.ruby_class_name == "Table":
                table = Table(inner_obj)
                converted_obj = table.serialize()
            else:
                converted_obj = self._rvdata2dict(inner_obj, serialize=False)

            if not isinstance(child_nodes, list):
                res[attr] = _serialize_obj(converted_obj, inner_obj)
            else:
                res.append(_serialize_obj(converted_obj, inner_obj))

        return _serialize_obj(res, rvdata_obj) if serialize else res

def main():
    parser = argparse.ArgumentParser(description='Process RVData files.')
    parser.add_argument('input_file', help='Input RVData or JSON file')
    parser.add_argument('output_file', help='Output file (JSON or YAML)')
    parser.add_argument('--to-json', action='store_true', help='Convert to JSON format')
    parser.add_argument('--to-yaml', action='store_true', help='Convert to YAML format')
    
    args = parser.parse_args()

    rvdata = RVDataFile()

    if args.input_file.endswith('.rvdata'):
        rvdata.from_rvdata(args.input_file)
    elif args.input_file.endswith('.json'):
        rvdata.from_json(args.input_file)
    else:
        print("Unsupported input file format. Only .rvdata and .json are allowed.")
        return

    if args.to_json:
        rvdata.to_json(args.output_file)
        print(f"Data converted to JSON and saved to {args.output_file} 📄")
    elif args.to_yaml:
        rvdata.to_yaml(args.output_file)
        print(f"Data converted to YAML and saved to {args.output_file} 📄")
    else:
        print("Please specify an output format with --to-json or --to-yaml.")

if __name__ == "__main__":
    main()
