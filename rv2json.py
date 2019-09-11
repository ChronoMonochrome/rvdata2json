import json
import yaml
from rubymarshal.reader import loads

class RVDataFile:
	_data = {}

	def __init__(self):
		pass

	def from_rvdata(self, input_file):
		self._data = loads(open(input_file, "rb").read())

	def from_json(self, input_file):
		pass

	def to_rvdata(self, output_file):
		pass

	def to_json(self, output_file):
		json_data = json.dumps(self._rvdata2dict(self._data), indent=4, sort_keys=True)
		open(output_file, "w").write(json_data)

	def to_yaml(self, output_file):
		data = self._rvdata2dict(self._data)
		with open(output_file, 'w') as f:
			yaml.dump(data, f, default_flow_style=False)


	def _serialize_obj(self, obj, type_):
		return {"val": obj, "type": type_.__name__}

	def _rvdata2dict(self, rvdata_obj):
		res = {}

		if not hasattr(rvdata_obj, "attributes") and type(rvdata_obj) not in [dict, list]:
			return rvdata_obj

		child_nodes = []
		if hasattr(rvdata_obj, "attributes"):
			child_nodes = rvdata_obj.attributes
		else:
			child_nodes = rvdata_obj

		if type(child_nodes) == list:
			res = []

		for attr in child_nodes:
			if type(child_nodes) != list:
				inner_obj = child_nodes[attr]
			else:
				inner_obj = attr

			inner_obj_type = type(inner_obj)

			if not hasattr(inner_obj, "attributes") and not inner_obj_type in [dict, list]:
				if inner_obj_type == bytes:
					inner_obj = repr(inner_obj)

				if type(child_nodes) != list:
					res[attr] = self._serialize_obj(inner_obj, inner_obj_type)
					#res[attr] = inner_obj
				else:
					#res.append(inner_obj)
					res.append(self._serialize_obj(inner_obj, inner_obj_type))
				continue

			converted_obj = self._rvdata2dict(inner_obj)

			if type(child_nodes) != list:
				res[attr] = self._serialize_obj(converted_obj, inner_obj_type)
				#res[attr] = converted_obj
			else:
				res.append(self._serialize_obj(converted_obj, inner_obj_type))
				#res.append(converted_obj)

		return res
