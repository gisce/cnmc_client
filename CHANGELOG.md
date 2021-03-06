# 0.3.0
- Created `utils/sips_update_by_zip.py` script
  - Desired to update SIPS information for all CUPS that belongs to a zipcode

# 0.2.0
- Package now is called "cnmc_client" instead of "cnmc"
- Client.fetch now accepts 'as_csv' flag
  - To return a csv.DictReader ready to be iterated instead of the response result
- API.method() now accept 'download' flag
  - Desired to handle downloads as a BytesIO instead of parse the result as JSON
  - Useful to in-memory files representation
- API.download() new wrapper method
  - Call API.method() as a GET request with download=True activated
- Created `utils/file_fetcher.py` script
  - Desired to show how to fetch SIPS files as bytes and iterable dicts
- Package cnmc_client is installable through setup.py file

# 0.1.0
- Initial CNMC client
  - The client
    - List files method
    - Fetch files method
    - Download file method //WIP
  - The CNMC API
    - OAuth1 session establishment
    - GET and POST HTTP actions
  - Basic Mamba specs for all functionalities
  - New requirements
    - Marshmallow
    - Munch
