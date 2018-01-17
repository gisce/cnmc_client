# 0.2.0
- Client.fetch now accepts 'as_csv' flag
  - To return a csv.reader ready to be iterated instead of the response result

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
