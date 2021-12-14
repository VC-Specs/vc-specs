import json
import sys
import argparse
import yaml


parser = argparse.ArgumentParser()
parser.add_argument("paths", nargs="+", help="JSON schema file path(s)")
parser.add_argument("-n", "--namespace",  help="Namespace of the context")
parser.add_argument("-t", "--type-map",  help="file path with type mapping for json paths")
args = parser.parse_args()
ns = "https://github.com/sunbird-specs/vc-specs"
#print(args)
overrides = {
    #"ContactDetails.email": "schema:email"
}

if args.type_map:
    with open(args.type_map, "r") as stream:
        try:
            overrides = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

other_mappings = {
    "cred": "https://www.w3.org/2018/credentials#",
    "dc": "http://purl.org/dc/terms",
    "powex": "https://github.com/sunbird-specs/vc-specs/work#",
    "schema": "https://www.schema.org",
    "sec": "https://w3id.org/security#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
type_map = {
    "string": "schema:Text",
    "number": "schema:Number",
    "boolean": "schema:Boolean"
}



def get_type(a, path):
    if "$ref" in a:
        ref = a["$ref"]
        if ref.startswith("#/definitions/"):
            return ref.replace("#/definitions/", ns + "#")
        return ref
    type_ = overrides.get(path, type_map.get(a["type"], "schema:Text"))
    return type_


def get_schema_(a, key, path="$"):
    if "properties" not in a.keys():
        return get_type(a, path)
    defs = {}
    defs.update({"@id": "%s#%s" % (ns, key)})
    properties_object = {"id": "@id", "@version": 1.1, "@protected": True}
    defs.update({"@context": properties_object})
    for k in a["properties"].keys():
        properties_object.update({k: get_schema_(a["properties"][k], k, path + "." + k)})
    return defs

def get_schema(o):
    assert o["$schema"] == 'http://json-schema.org/draft-07/schema'
    schema = {}
    schema_ctx = {"@version":"1.1", "@protected":True}
    schema.update({"@context": schema_ctx})
    for key in o["definitions"]:
        schema_ctx.update({key: get_schema_(o["definitions"][key], key, key)})
    return schema

#print(json.dumps(get_schema(o), indent="  "))
for filename in args.paths:
    print("processing %s"%filename)
    with open(filename, 'r') as content_file:
        content = content_file.read()
    o = json.loads(content)
    assert o["$schema"] == 'http://json-schema.org/draft-07/schema'
    with open(filename.replace(".json", ".jsonld"), "w") as f:
        f.write(json.dumps(get_schema(o), indent="  "))