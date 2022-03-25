import jsonschema
import unittest
import json



class JsonManager:

    @staticmethod
    def validate(schema, data):
        '''
        Validate schema file or json against file or json

        '''
        if isinstance(schema, str):
            f = open(schema)
            schema = json.load(f)
            f.close()

        if isinstance(data, str):
            f = open(data)
            data = json.load(f)
            f.close()

        try:
            jsonschema.validate(data, schema=schema)
            return True
        except Exception as e:
            raise Exception(e.__str__)
            return False


class TestJsonManager(unittest.TestCase):
    def test_validate(self):
        schema = {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "name": {"type": "string"},
            }
        }
        data = {
            "name": "ABC",
            "price": 1.0
        }
        try:
            self.assertTrue(JsonManager.validate(schema, data))
        except Exception as e:
            print(e.message)
            self.fail()
if __name__ == '__main__':
    unittest.main()