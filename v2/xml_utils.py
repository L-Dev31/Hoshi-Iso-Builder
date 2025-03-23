# functions for general XML files
import file_ops
from lxml import etree

# function to check if a XML file is well formatted
def check_xml_well_format(xml_path):
  
  # check params
  if (file_ops.is_file(xml_path) == False):
    return False
  
  # load the xml file and check for syntax errors
  # generic parser
  generic_parser = etree.XMLParser(ns_clean = True, remove_comments = True)
  xml = None
  try:
    xml = etree.parse(xml_path, generic_parser)
  # some errors are not saved on parser's error_log for some reason
  except etree.XMLSyntaxError as e:
    print("\nSYNTAX ERRORS ON XML:")
    print(e)
    return False
  # print the parser error_log errors
  except:
    print("\nOTHER ERRORS ON XML:")
    for error in generic_parser.error_log:
      print("Line %s || %s" % (error.line, error.message))
    return False
  
  # all good!
  return True

# function to check if an schema (XSD) file is well formatted
def check_sch_well_format(xsd_path):
  
  # check params
  if (check_xml_well_format(xsd_path) == False):
    return False
  
  # load the XMLSchema.xsd as a parser for the schema files
  schema_tree = etree.parse("XMLSchema.xsd")
  schema_schema = etree.XMLSchema(schema_tree)
  schema_parser = etree.XMLParser(schema = schema_schema)

  # load the custom schema file and check if it has errors
  try:
    custom_schema_tree = etree.parse(xsd_path, schema_parser)
    custom_schema_schema = etree.XMLSchema(custom_schema_tree)
  # some errors are not saved on parser's error_log for some reason
  except etree.XMLSyntaxError as e:
    print("\nSYNTAX ERRORS ON XSD:")
    print(e)
    return False
  except etree.XMLSchemaParseError as e:
    print("\nSCHEMA PARSING ERRORS ON XSD:")
    print(e)
    return False
  # print the parser error_log errors
  except:
    print("\nOTHER ERRORS ON XSD:")
    for error in schema_parser.error_log:
      print("Line %s || %s" % (error.line, error.message))
    return False
  
  # all good!
  return True

# function to check an XML against an schema (XSD)
def check_with_sch(xml_path, xsd_path):
  # check params
  if ((check_xml_well_format(xml_path) == False) or (check_sch_well_format(xsd_path) == False)):
    return False
  
  # load the collada file and check for errors agaisnt the custom schema
  schema_tree = etree.parse(xsd_path)
  schema_schema = etree.XMLSchema(schema_tree)
  schema_parser = etree.XMLParser(schema = schema_schema)
  try:
    xml = etree.parse(xml_path, schema_parser)
  # some errors are not saved on parser's error_log for some reason
  except etree.XMLSyntaxError as e:
    print("\nSYNTAX ERRORS ON CUSTOM SCHEMA CHECKING XML:")
    print(e)
    return False
  # print the parser error_log errors
  except etree.XMLSchemaValidateError:
    print("\nOTHER ERRORS ON CUSTOM SCHEMA CHECKING XML:")
    for error in custom_schema_parser.error_log:
      print("Line %s || %s" % (error.line, error.message))
    return False
  
  # done!
  return True
