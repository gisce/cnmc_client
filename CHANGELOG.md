# 0.2.0
- Client.fetch now accepts 'as_csv' flag
  - To return a csv.reader ready to be iterated instead of the response result
- API.method() now accept 'download' flag
  - Desired to handle downloads as a BytesIO instead of parse the result as JSON
  - Useful to in-memory files representation
- API.download() new wrapper method
  - Call API.method() as a GET request with download=True activated

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
